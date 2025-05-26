from agents.reception_agent import ReceptionAgent
from agents.booking_agent import BookingAgent
from agents.scheduler_agent import SchedulerAgent
from agents.faq_agent import FAQAgent
from agents.emergency_agent import EmergencyAgent
from agents.feedback_agent import FeedbackAgent
from agents.hr_agent import HRAgent
from agents.it_agent import ITAgent
from agents.visitor_agent import VisitorAgent
from agent_graph import AgentGraph


class ConversationAgentGraph():
    def create_agent_graph() -> AgentGraph:
        reception_agent = ReceptionAgent()
        booking_agent = BookingAgent()
        scheduler_agent = SchedulerAgent()
        faq_agent = FAQAgent()
        emergency_agent = EmergencyAgent()
        feedback_agent = FeedbackAgent()
        hr_agent = HRAgent()
        it_agent = ITAgent()
        visitor_agent = VisitorAgent()

        # Build the agent graph
        agent_graph = AgentGraph(
            reception_agent,
            transition_rules={
                "booking": "booking_agent",
                "faq": "faq_agent",
                "emergency": "emergency_agent",
                "hr": "hr_agent",
                "it": "it_agent",
                "visitor": "visitor_agent",
                "feedback": "feedback_agent"
            },
            intent_patterns={}
        )

        # Add all primary agents as children of reception_agent first
        agent_graph.add_agent(
            parent_agent_name="reception_agent",
            agent=booking_agent,
            transition_rules={
                "scheduler": "scheduler_agent",
                "faq": "faq_agent",
                "feedback": "feedback_agent",
                "reception": "reception_agent"
            }
        )
        agent_graph.add_agent(
            parent_agent_name="reception_agent",
            agent=faq_agent,
            transition_rules={
                "reception": "reception_agent",
                "feedback": "feedback_agent",
                "hr": "hr_agent",
                "it": "it_agent"
            }
        )
        agent_graph.add_agent(
            parent_agent_name="reception_agent",
            agent=emergency_agent,
            transition_rules={
                "reception": "reception_agent",
                "feedback": "feedback_agent"
            }
        )
        agent_graph.add_agent(
            parent_agent_name="reception_agent",
            agent=hr_agent,
            transition_rules={
                "faq": "faq_agent",
                "reception": "reception_agent",
                "feedback": "feedback_agent"
            }
        )
        agent_graph.add_agent(
            parent_agent_name="reception_agent",
            agent=it_agent,
            transition_rules={
                "faq": "faq_agent",
                "reception": "reception_agent",
                "feedback": "feedback_agent"
            }
        )
        agent_graph.add_agent(
            parent_agent_name="reception_agent",
            agent=visitor_agent,
            transition_rules={
                "booking": "booking_agent",
                "reception": "reception_agent",
                "feedback": "feedback_agent"
            }
        )
        agent_graph.add_agent(
            parent_agent_name="booking_agent",
            agent=scheduler_agent,
            transition_rules={
                "reception": "reception_agent",
                "feedback": "feedback_agent"
            }
        )
        # Add feedback_agent only once as a child of reception_agent
        agent_graph.add_agent(
            parent_agent_name="reception_agent",
            agent=feedback_agent,
            transition_rules={
                "reception": "reception_agent"
            }
        )
        return agent_graph