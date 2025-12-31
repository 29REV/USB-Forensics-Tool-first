#!/usr/bin/env python3
"""
AI Reporter - Narrative Report Generation

Generates professional forensic narrative reports using LLM APIs.
Transforms raw logs and analysis data into human-readable investigation summaries.

No modifications to base tool required. Standalone extension module.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AIReporter:
    """
    AI-powered narrative report generator for forensic investigations.
    
    Supports:
    - OpenAI GPT API
    - Anthropic Claude API
    - Local LLM fallback (structured templates)
    - Custom narrative formatting
    """
    
    # Report templates for cases where LLM is unavailable
    REPORT_TEMPLATES = {
        'incident_analysis': """
INCIDENT ANALYSIS REPORT
Generated: {timestamp}

EXECUTIVE SUMMARY
-----------------
{summary}

INCIDENT TIMELINE
-----------------
{timeline}

DEVICES INVOLVED
----------------
{devices}

FORENSIC FINDINGS
-----------------
{findings}

RISK ASSESSMENT
---------------
{risk_assessment}

RECOMMENDATIONS
----------------
{recommendations}
        """,
        
        'investigation': """
USB FORENSIC INVESTIGATION REPORT
Generated: {timestamp}

INVESTIGATION OVERVIEW
---------------------
Device: {device_name}
Serial: {device_serial}
Investigation Period: {start_time} to {end_time}

KEY FINDINGS
-----------
{key_findings}

DETAILED TIMELINE
-----------------
{timeline}

DATA ANALYSIS
-----------
{analysis}

CONCLUSIONS
-----------
{conclusions}

EVIDENCE CHAIN
--------------
{evidence_chain}
        """,
        
        'executive_summary': """
EXECUTIVE SUMMARY - USB FORENSIC INVESTIGATION
{timestamp}

SITUATION
---------
{situation}

KEY FINDINGS
-----------
{findings}

IMPACT ASSESSMENT
-----------------
{impact}

RECOMMENDED ACTIONS
-------------------
{actions}
        """
    }
    
    # Common LLM API configurations
    LLM_PROVIDERS = {
        'openai': {
            'name': 'OpenAI GPT-4',
            'endpoint': 'https://api.openai.com/v1/chat/completions',
            'model': 'gpt-4',
            'requires_key': True
        },
        'anthropic': {
            'name': 'Anthropic Claude',
            'endpoint': 'https://api.anthropic.com/v1/messages',
            'model': 'claude-3-opus-20240229',
            'requires_key': True
        },
        'local': {
            'name': 'Local Template Engine',
            'endpoint': 'local',
            'model': 'template-based',
            'requires_key': False
        }
    }
    
    def __init__(self, llm_provider: str = 'local', api_key: str = None):
        """
        Initialize AI Reporter.
        
        Args:
            llm_provider: LLM provider ('openai', 'anthropic', 'local')
            api_key: API key for LLM provider (if required)
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.use_local_templates = llm_provider == 'local' or api_key is None
        
        logger.info(f"AIReporter initialized with provider: {llm_provider}")
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming IPI message from bridge.
        
        Args:
            message: IPI message with action and data
            
        Returns:
            Response dictionary
        """
        action = message.get('action', 'unknown')
        data = message.get('data', {})
        
        try:
            if action == 'generate_report':
                return self.generate_narrative_report(
                    raw_logs=data.get('raw_logs', []),
                    analysis_data=data.get('analysis_data', {})
                )
            
            elif action == 'executive_summary':
                return self.generate_executive_summary(
                    analysis_results=data.get('analysis_results', {})
                )
            
            elif action == 'timeline_narrative':
                return self.generate_timeline_narrative(
                    events=data.get('events', []),
                    context=data.get('context', {})
                )
            
            elif action == 'incident_report':
                return self.generate_incident_report(
                    incident_data=data.get('incident_data', {}),
                    evidence=data.get('evidence', [])
                )
            
            else:
                return self._error(f"Unknown action: {action}")
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._error(str(e))
    
    def _error(self, message: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            'status': 'error',
            'error': message,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_narrative_report(self, raw_logs: List[str], analysis_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate narrative report from raw logs.
        
        Args:
            raw_logs: List of raw log entries
            analysis_data: Optional analysis context
            
        Returns:
            Formatted narrative report
        """
        try:
            if analysis_data is None:
                analysis_data = {}
            
            # Prepare data
            logs_text = self._format_logs(raw_logs)
            
            # Generate narrative
            if self.use_local_templates:
                narrative = self._generate_narrative_from_logs(raw_logs, analysis_data)
            else:
                narrative = self._query_llm_for_narrative(raw_logs, analysis_data)
            
            return {
                'status': 'success',
                'report': narrative,
                'format': 'narrative',
                'logs_analyzed': len(raw_logs),
                'timestamp': datetime.now().isoformat(),
                'llm_provider': self.llm_provider,
                'provider_note': 'Using local template engine - Deploy with API key for enhanced narratives'
            }
        
        except Exception as e:
            logger.error(f"Error generating narrative report: {e}")
            return self._error(str(e))
    
    def generate_executive_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate executive summary for investigation.
        
        Args:
            analysis_results: Analysis results from base tool
            
        Returns:
            Executive summary text
        """
        try:
            # Extract key information
            summary_points = self._extract_summary_points(analysis_results)
            
            # Generate summary
            if self.use_local_templates:
                summary = self._generate_summary_template(summary_points, analysis_results)
            else:
                summary = self._query_llm_for_summary(analysis_results)
            
            return {
                'status': 'success',
                'summary': summary,
                'key_points': summary_points,
                'timestamp': datetime.now().isoformat(),
                'analysis_context': {
                    'total_devices': len(analysis_results.get('devices', [])),
                    'investigation_duration': analysis_results.get('duration', 'unknown'),
                    'findings_count': len(analysis_results.get('findings', []))
                }
            }
        
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return self._error(str(e))
    
    def generate_timeline_narrative(self, events: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate narrative timeline from events.
        
        Args:
            events: List of timeline events
            context: Optional context information
            
        Returns:
            Timeline narrative
        """
        try:
            if context is None:
                context = {}
            
            # Sort events by timestamp
            sorted_events = sorted(
                events,
                key=lambda x: x.get('timestamp', ''),
                reverse=False
            )
            
            # Generate narrative
            narrative = self._build_timeline_narrative(sorted_events, context)
            
            return {
                'status': 'success',
                'narrative': narrative,
                'events_included': len(sorted_events),
                'timeline_span': f"{sorted_events[0].get('timestamp', '')} to {sorted_events[-1].get('timestamp', '')}",
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating timeline narrative: {e}")
            return self._error(str(e))
    
    def generate_incident_report(self, incident_data: Dict[str, Any], evidence: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate formal incident report.
        
        Args:
            incident_data: Incident information
            evidence: List of evidence items
            
        Returns:
            Formatted incident report
        """
        try:
            if evidence is None:
                evidence = []
            
            report_sections = {
                'executive_summary': self._format_incident_summary(incident_data),
                'incident_details': self._format_incident_details(incident_data),
                'evidence_analysis': self._format_evidence_analysis(evidence),
                'risk_assessment': self._format_risk_assessment(incident_data),
                'recommendations': self._format_recommendations(incident_data, evidence)
            }
            
            # Generate narrative
            if self.use_local_templates:
                report = self._generate_incident_report_template(report_sections)
            else:
                report = self._query_llm_for_incident_report(incident_data, evidence)
            
            return {
                'status': 'success',
                'report': report,
                'sections': report_sections,
                'timestamp': datetime.now().isoformat(),
                'incident_id': incident_data.get('incident_id', 'UNKNOWN'),
                'severity': incident_data.get('severity', 'UNKNOWN')
            }
        
        except Exception as e:
            logger.error(f"Error generating incident report: {e}")
            return self._error(str(e))
    
    # ═══════════════════════════════════════════════════════════════
    # Report generation methods
    # ═══════════════════════════════════════════════════════════════
    
    def _format_logs(self, logs: List[str]) -> str:
        """Format log list into readable text."""
        return "\n".join(f"  • {log}" for log in logs)
    
    def _generate_narrative_from_logs(self, logs: List[str], analysis_data: Dict[str, Any]) -> str:
        """Generate narrative from logs using template."""
        narrative = "FORENSIC NARRATIVE REPORT\n"
        narrative += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        narrative += "="*60 + "\n\n"
        
        narrative += "INVESTIGATION OVERVIEW\n"
        narrative += "-"*40 + "\n"
        
        if analysis_data.get('device_name'):
            narrative += f"Device: {analysis_data['device_name']}\n"
        if analysis_data.get('device_serial'):
            narrative += f"Serial: {analysis_data['device_serial']}\n"
        
        narrative += f"\nTotal Events: {len(logs)}\n\n"
        
        narrative += "CHRONOLOGICAL EVENTS\n"
        narrative += "-"*40 + "\n"
        
        # Group logs by type
        activity_logs = [l for l in logs if 'activity' in l.lower()]
        connection_logs = [l for l in logs if 'connect' in l.lower() or 'mount' in l.lower()]
        error_logs = [l for l in logs if 'error' in l.lower() or 'warn' in l.lower()]
        
        if connection_logs:
            narrative += "\n[CONNECTION EVENTS]\n"
            for log in connection_logs:
                narrative += f"  • {log}\n"
        
        if activity_logs:
            narrative += "\n[ACTIVITY EVENTS]\n"
            for log in activity_logs[:10]:  # Limit to 10
                narrative += f"  • {log}\n"
            if len(activity_logs) > 10:
                narrative += f"  ... and {len(activity_logs) - 10} more activity events\n"
        
        if error_logs:
            narrative += "\n[ALERTS/ERRORS]\n"
            for log in error_logs:
                narrative += f"  ⚠ {log}\n"
        
        narrative += "\n" + "-"*40 + "\n"
        narrative += "ANALYSIS CONCLUSIONS\n\n"
        narrative += self._generate_conclusions(logs, analysis_data)
        
        return narrative
    
    def _generate_conclusions(self, logs: List[str], analysis_data: Dict[str, Any]) -> str:
        """Generate analysis conclusions."""
        conclusions = []
        
        # Analyze for patterns
        total_events = len(logs)
        conclusions.append(f"• Total events recorded: {total_events}")
        
        if any('error' in l.lower() for l in logs):
            conclusions.append("• Suspicious errors detected during operation")
        
        if any('disconnect' in l.lower() for l in logs):
            conclusions.append("• Device was safely disconnected")
        else:
            conclusions.append("• WARNING: No proper disconnect sequence recorded")
        
        if analysis_data.get('risk_score', 0) > 0.5:
            conclusions.append("• Device exhibits suspicious characteristics")
        
        return "\n".join(conclusions)
    
    def _build_timeline_narrative(self, events: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Build narrative timeline from events."""
        narrative = "TIMELINE NARRATIVE\n"
        narrative += "="*60 + "\n\n"
        
        for i, event in enumerate(events, 1):
            timestamp = event.get('timestamp', 'Unknown')
            event_type = event.get('event_type', 'Unknown')
            description = event.get('description', 'No description')
            
            narrative += f"{i}. [{timestamp}] {event_type.upper()}\n"
            narrative += f"   {description}\n"
            
            if event.get('details'):
                narrative += f"   Details: {str(event['details'])[:100]}...\n"
            
            narrative += "\n"
        
        return narrative
    
    def _extract_summary_points(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract key summary points from analysis."""
        points = []
        
        # Extract from findings
        findings = analysis_results.get('findings', [])
        if findings:
            points.append(f"Found {len(findings)} significant findings")
            for finding in findings[:3]:
                points.append(f"• {finding}")
        
        # Extract from devices
        devices = analysis_results.get('devices', [])
        if devices:
            points.append(f"Analyzed {len(devices)} USB devices")
        
        # Extract risk information
        risk_score = analysis_results.get('risk_score')
        if risk_score is not None:
            risk_level = "LOW" if risk_score < 0.3 else "MEDIUM" if risk_score < 0.6 else "HIGH"
            points.append(f"Overall risk assessment: {risk_level} ({risk_score:.2f})")
        
        return points
    
    def _generate_summary_template(self, summary_points: List[str], analysis_results: Dict[str, Any]) -> str:
        """Generate summary from template."""
        summary = "EXECUTIVE SUMMARY\n"
        summary += "="*60 + "\n\n"
        
        summary += "KEY FINDINGS\n"
        summary += "-"*40 + "\n"
        for point in summary_points:
            summary += f"{point}\n"
        
        summary += "\n" + "-"*40 + "\n"
        summary += "RECOMMENDATIONS\n\n"
        
        risk_score = analysis_results.get('risk_score', 0)
        if risk_score > 0.7:
            summary += "• Immediate isolation of device recommended\n"
            summary += "• Escalate to security team\n"
            summary += "• Preserve evidence for detailed analysis\n"
        elif risk_score > 0.4:
            summary += "• Monitor device closely\n"
            summary += "• Document all activity\n"
            summary += "• Consider quarantine for further analysis\n"
        else:
            summary += "• Device appears safe\n"
            summary += "• Continue standard monitoring\n"
            summary += "• Document findings in security log\n"
        
        return summary
    
    def _format_incident_summary(self, incident_data: Dict[str, Any]) -> str:
        """Format incident summary section."""
        return f"""
Incident ID: {incident_data.get('incident_id', 'Unknown')}
Severity: {incident_data.get('severity', 'Unknown')}
Date Reported: {incident_data.get('date_reported', datetime.now().isoformat())}
Status: {incident_data.get('status', 'Under Investigation')}
        """
    
    def _format_incident_details(self, incident_data: Dict[str, Any]) -> str:
        """Format incident details section."""
        details = "\nINCIDENT DETAILS\n"
        details += "-"*40 + "\n"
        details += f"Description: {incident_data.get('description', 'N/A')}\n"
        details += f"Affected Systems: {incident_data.get('affected_systems', 'Unknown')}\n"
        details += f"Initial Detection: {incident_data.get('initial_detection', 'Unknown')}\n"
        return details
    
    def _format_evidence_analysis(self, evidence: List[Dict[str, Any]]) -> str:
        """Format evidence analysis section."""
        analysis = "\nEVIDENCE ANALYSIS\n"
        analysis += "-"*40 + "\n"
        analysis += f"Total Evidence Items: {len(evidence)}\n\n"
        
        for item in evidence[:5]:  # Show first 5 items
            analysis += f"• {item.get('type', 'Unknown')}: {item.get('description', 'N/A')}\n"
        
        if len(evidence) > 5:
            analysis += f"\n... and {len(evidence) - 5} more evidence items\n"
        
        return analysis
    
    def _format_risk_assessment(self, incident_data: Dict[str, Any]) -> str:
        """Format risk assessment section."""
        risk_score = incident_data.get('risk_score', 0)
        
        if risk_score > 0.7:
            risk_level = "CRITICAL"
        elif risk_score > 0.5:
            risk_level = "HIGH"
        elif risk_score > 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return f"\nRISK ASSESSMENT\n-"*40 + f"\nRisk Level: {risk_level}\nRisk Score: {risk_score:.2f}\n"
    
    def _format_recommendations(self, incident_data: Dict[str, Any], evidence: List[Dict[str, Any]]) -> str:
        """Format recommendations section."""
        recommendations = "\nRECOMMENDATIONS\n"
        recommendations += "-"*40 + "\n"
        
        risk_score = incident_data.get('risk_score', 0)
        
        if risk_score > 0.7:
            recommendations += "1. IMMEDIATE: Isolate affected device\n"
            recommendations += "2. URGENT: Notify security operations\n"
            recommendations += "3. Preserve all evidence\n"
            recommendations += "4. Conduct full forensic analysis\n"
        elif risk_score > 0.4:
            recommendations += "1. Monitor affected device closely\n"
            recommendations += "2. Document all activity\n"
            recommendations += "3. Review system logs for similar activity\n"
        else:
            recommendations += "1. Continue standard monitoring\n"
            recommendations += "2. Document findings\n"
            recommendations += "3. Update security baseline\n"
        
        return recommendations
    
    def _generate_incident_report_template(self, sections: Dict[str, str]) -> str:
        """Generate incident report from template."""
        report = "INCIDENT FORENSIC REPORT\n"
        report += "="*60 + "\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "="*60 + "\n\n"
        
        for section_name, section_content in sections.items():
            report += section_content + "\n\n"
        
        return report
    
    # ═══════════════════════════════════════════════════════════════
    # LLM query methods (placeholders for API integration)
    # ═══════════════════════════════════════════════════════════════
    
    def _query_llm_for_narrative(self, logs: List[str], analysis_data: Dict[str, Any]) -> str:
        """Query LLM for narrative (requires API key)."""
        logger.warning("LLM narrative generation not available without API key")
        return self._generate_narrative_from_logs(logs, analysis_data)
    
    def _query_llm_for_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Query LLM for summary (requires API key)."""
        logger.warning("LLM summary generation not available without API key")
        summary_points = self._extract_summary_points(analysis_results)
        return self._generate_summary_template(summary_points, analysis_results)
    
    def _query_llm_for_incident_report(self, incident_data: Dict[str, Any], evidence: List[Dict[str, Any]]) -> str:
        """Query LLM for incident report (requires API key)."""
        logger.warning("LLM incident report generation not available without API key")
        sections = {
            'executive_summary': self._format_incident_summary(incident_data),
            'incident_details': self._format_incident_details(incident_data),
            'evidence_analysis': self._format_evidence_analysis(evidence),
            'risk_assessment': self._format_risk_assessment(incident_data),
            'recommendations': self._format_recommendations(incident_data, evidence)
        }
        return self._generate_incident_report_template(sections)


# ═══════════════════════════════════════════════════════════════════════════
# USAGE IN BASE TOOL
# ═══════════════════════════════════════════════════════════════════════════

def example_usage():
    """
    Example of how to use AIReporter from base tool.
    """
    from extensions.bridge import BaseToolExtensionInterface
    
    interface = BaseToolExtensionInterface()
    
    # Generate narrative report
    logs = [
        "Device connected at 10:00 AM",
        "5 files copied to device",
        "Device activity detected for 2 hours",
        "Device safely ejected at 12:00 PM"
    ]
    
    print("\n=== Generating Narrative Report ===")
    result = interface.generate_narrative_report(logs)
    print(result.get('report'))


if __name__ == '__main__':
    print("AI Reporter - Narrative Report Generator")
    print("="*70)
    
    reporter = AIReporter()
    print(f"✓ AIReporter initialized")
    print(f"✓ LLM Provider: {reporter.llm_provider}")
    print(f"✓ Using: {'Local template engine' if reporter.use_local_templates else 'LLM API'}")
    print(f"\nReport templates available:")
    for template_name in AIReporter.REPORT_TEMPLATES.keys():
        print(f"  • {template_name}")
    print("\nTo use in your base tool:")
    print("  from extensions.bridge import BaseToolExtensionInterface")
    print("  interface = BaseToolExtensionInterface()")
    print("  report = interface.generate_narrative_report(logs)")
