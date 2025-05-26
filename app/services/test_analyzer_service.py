import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import google.generativeai as genai
from dotenv import load_dotenv

from app.schemas.test import TestRunResult, TestAnalysisResult
from app.services.log_service import LogService
from app.services.test_service import TestService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TestAnalyzerService:
    """Service for analyzing test results using Gemini AI"""
    
    def __init__(self, log_service: LogService, test_service: TestService):
        """Initialize test analyzer service with required dependencies"""
        self.log_service = log_service
        self.test_service = test_service
        self.gemini_model = self._get_gemini_model()
    
    def _get_gemini_model(self):
        """Configure and return the Gemini model"""
        try:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                logger.error("GEMINI_API_KEY environment variable not found")
                return None
            
            # Configure Gemini API
            genai.configure(api_key=gemini_api_key)
            
            # Get Gemini model
            model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Successfully initialized Gemini model")
            return model
            
        except Exception as e:
            logger.exception(f"Error initializing Gemini model: {str(e)}")
            return None
    
    async def analyze_test_run(self, test_run_id: str, include_logs: bool = True) -> TestAnalysisResult:
        """Analyze a test run using Gemini AI"""
        logger.info(f"Analyzing test run: {test_run_id}")
        
        # Get test run metadata
        test_run = await self.test_service.get_test_run(test_run_id)
        if not test_run:
            raise ValueError(f"Test run with ID {test_run_id} not found")
        
        # Get associated logs if requested
        logs = []
        if include_logs and test_run.log_ids:
            logs = await self._get_logs_for_test_run(test_run)
        
        # Read test report file
        report_data = await self._read_test_report(test_run)
        
        # Generate analysis using Gemini
        analysis_result = await self._generate_analysis(test_run, logs, report_data)
        
        # Save analysis to disk
        self._save_analysis(test_run, analysis_result)
        
        return analysis_result
    
    async def _get_logs_for_test_run(self, test_run: TestRunResult) -> List[Dict[str, Any]]:
        """Get logs associated with a test run"""
        logs = []
        
        for log_id in test_run.log_ids:
            try:
                log = await self.log_service.get_log_by_id(log_id)
                if log:
                    logs.append(log.dict())
            except Exception as e:
                logger.error(f"Error retrieving log {log_id}: {str(e)}")
        
        return logs
    
    async def _read_test_report(self, test_run: TestRunResult) -> Optional[Dict[str, Any]]:
        """Read the test report file"""
        project_dir = os.path.join(self.test_service.test_results_dir, test_run.project_id)
        test_run_dir = os.path.join(project_dir, test_run.id)
        report_path = os.path.join(test_run_dir, "report.json")
        
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading test report: {str(e)}")
        
        return None
    
    async def _generate_analysis(
        self, 
        test_run: TestRunResult, 
        logs: List[Dict[str, Any]], 
        report_data: Optional[Dict[str, Any]]
    ) -> TestAnalysisResult:
        """Generate test analysis using Gemini AI"""
        if not self.gemini_model:
            return TestAnalysisResult(
                test_run_id=test_run.id,
                project_id=test_run.project_id,
                service_id=test_run.service_id,
                analysis="Unable to generate analysis: Gemini model not initialized",
                summary="Analysis failed",
                success=False,
                created_at=datetime.now()
            )
        
        # Prepare the prompt for Gemini
        prompt = self._create_analysis_prompt(test_run, logs, report_data)
        
        try:
            # Call Gemini API
            logger.info("Calling Gemini API to analyze test results...")
            response = self.gemini_model.generate_content(prompt)
            
            if not hasattr(response, 'text'):
                logger.error("Unexpected response format from Gemini API")
                return TestAnalysisResult(
                    test_run_id=test_run.id,
                    project_id=test_run.project_id,
                    service_id=test_run.service_id,
                    analysis="Error: Unexpected response format from Gemini API",
                    summary="Analysis failed",
                    success=False,
                    created_at=datetime.now()
                )
            
            # Process the response to extract structured information
            analysis_text, summary, issues, suggestions = self._process_gemini_response(response.text)
            
            return TestAnalysisResult(
                test_run_id=test_run.id,
                project_id=test_run.project_id,
                service_id=test_run.service_id,
                analysis=analysis_text,
                summary=summary,
                issues_detected=issues,
                suggestions=suggestions,
                success=True,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.exception(f"Error calling Gemini API: {str(e)}")
            return TestAnalysisResult(
                test_run_id=test_run.id,
                project_id=test_run.project_id,
                service_id=test_run.service_id,
                analysis=f"Error generating analysis: {str(e)}",
                summary="Analysis failed",
                success=False,
                created_at=datetime.now()
            )
    
    def _create_analysis_prompt(
        self, 
        test_run: TestRunResult, 
        logs: List[Dict[str, Any]], 
        report_data: Optional[Dict[str, Any]]
    ) -> str:
        """Create a prompt for Gemini to analyze test results"""
        # Build a comprehensive prompt with test metadata, results, and logs
        prompt = f"""
        You are an expert test analyzer for microservices. Analyze the following test run results and provide insights.
        
        ## Test Run Metadata
        - Test Run ID: {test_run.id}
        - Project ID: {test_run.project_id}
        - Service ID: {test_run.service_id}
        - Test Path: {test_run.test_path}
        - Status: {test_run.status.value}
        - Start Time: {test_run.start_time}
        - End Time: {test_run.end_time if test_run.end_time else 'N/A'}
        - Duration: {test_run.duration_seconds if test_run.duration_seconds else 'N/A'} seconds
        - Total Tests: {test_run.total_tests}
        - Passed Tests: {test_run.passed_tests}
        - Failed Tests: {test_run.failed_tests}
        - Error Tests: {test_run.error_tests}
        - Skipped Tests: {test_run.skipped_tests}
        
        """
        
        # Add test report data if available
        if report_data:
            prompt += """
            ## Test Report
            """
            
            if 'tests' in report_data:
                prompt += "\n### Test Cases\n"
                for i, test in enumerate(report_data['tests']):
                    test_id = test.get('nodeid', 'Unknown')
                    outcome = test.get('outcome', 'Unknown')
                    duration = test.get('duration', 'Unknown')
                    
                    prompt += f"- Test {i+1}: {test_id}\n"
                    prompt += f"  - Outcome: {outcome}\n"
                    prompt += f"  - Duration: {duration} seconds\n"
                    
                    if outcome == 'failed' and 'call' in test:
                        call_data = test['call']
                        if 'longrepr' in call_data:
                            error_message = call_data['longrepr']
                            prompt += f"  - Error: {error_message}\n"
        
        # Add logs if available
        if logs:
            prompt += """
            ## Logs
            """
            
            # Sort logs by timestamp if available
            logs_with_time = [(log.get('timestamp', ''), log) for log in logs]
            logs_with_time.sort()
            sorted_logs = [log for _, log in logs_with_time]
            
            for log in sorted_logs[-20:]:  # Limit to last 20 logs to keep prompt size reasonable
                message = log.get('message', 'No message')
                severity = log.get('severity', 'INFO')
                source = log.get('source', 'Unknown')
                timestamp = log.get('timestamp', 'Unknown')
                
                prompt += f"- [{timestamp}] [{severity}] [{source}] {message}\n"
        
        # Add instructions for the analysis
        prompt += """
        ## Analysis Instructions
        
        Please analyze these test results and provide:
        
        1. A comprehensive analysis of the test run, including:
           - Overall assessment of the test run
           - Identification of key issues or failures
           - Patterns in test failures (if any)
           - Potential root causes for failures
        
        2. A brief summary of your findings (1-2 sentences)
        
        3. A list of specific issues detected, formatted as:
           ISSUES:
           - [issue description 1]
           - [issue description 2]
           ...
        
        4. A list of suggestions for improvement, formatted as:
           SUGGESTIONS:
           - [suggestion 1]
           - [suggestion 2]
           ...
        
        Focus on providing actionable insights that would help developers fix the issues.
        """
        
        return prompt
    
    def _process_gemini_response(self, response_text: str) -> tuple:
        """Process Gemini response to extract structured information"""
        # Default values
        analysis = response_text
        summary = "Test analysis completed"
        issues = []
        suggestions = []
        
        # Extract issues section
        issues_start = response_text.find("ISSUES:")
        if issues_start != -1:
            issues_end = response_text.find("SUGGESTIONS:")
            if issues_end == -1:
                issues_end = len(response_text)
            
            issues_text = response_text[issues_start + 7:issues_end].strip()
            issues = [issue.strip()[2:].strip() for issue in issues_text.split('\n') if issue.strip().startswith('-')]
        
        # Extract suggestions section
        suggestions_start = response_text.find("SUGGESTIONS:")
        if suggestions_start != -1:
            suggestions_text = response_text[suggestions_start + 12:].strip()
            suggestions = [suggestion.strip()[2:].strip() for suggestion in suggestions_text.split('\n') if suggestion.strip().startswith('-')]
        
        # Extract summary (assuming it's in the first few lines)
        lines = response_text.split('\n')
        for line in lines[:10]:
            if len(line.strip()) > 20 and len(line.strip()) < 200 and not line.startswith('#') and not line.startswith('-'):
                summary = line.strip()
                break
        
        # Clean up the analysis text
        if issues_start != -1:
            analysis = response_text[:issues_start].strip()
        
        return analysis, summary, issues, suggestions
    
    def _save_analysis(self, test_run: TestRunResult, analysis: TestAnalysisResult) -> None:
        """Save analysis results to disk"""
        project_dir = os.path.join(self.test_service.test_results_dir, test_run.project_id)
        test_run_dir = os.path.join(project_dir, test_run.id)
        
        analysis_path = os.path.join(test_run_dir, "analysis.json")
        
        # Convert analysis to dict and handle datetime serialization
        analysis_dict = analysis.dict()
        if analysis.created_at:
            analysis_dict["created_at"] = analysis.created_at.isoformat()
            
        with open(analysis_path, 'w') as f:
            json.dump(analysis_dict, f, indent=2)
    
    async def get_analysis(self, test_run_id: str) -> Optional[TestAnalysisResult]:
        """Get the analysis for a test run if it exists"""
        # Get test run metadata
        test_run = await self.test_service.get_test_run(test_run_id)
        if not test_run:
            return None
        
        # Check if analysis file exists
        project_dir = os.path.join(self.test_service.test_results_dir, test_run.project_id)
        test_run_dir = os.path.join(project_dir, test_run.id)
        analysis_path = os.path.join(test_run_dir, "analysis.json")
        
        if os.path.exists(analysis_path):
            try:
                with open(analysis_path, 'r') as f:
                    analysis_data = json.load(f)
                    return TestAnalysisResult(**analysis_data)
            except Exception as e:
                logger.error(f"Error reading analysis file: {str(e)}")
        
        return None
