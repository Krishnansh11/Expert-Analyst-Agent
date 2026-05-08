from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
import os
from expert_analyst.tools.Telegram_Notify import TelegramNotificationTool

from dotenv import load_dotenv
load_dotenv(override=True)

# llm = LLM(
#     model="groq/llama-3.3-70b-versatile",
#     api_key=os.getenv("GROQ_API_KEY")
# )
llm = LLM(
    model="google/gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

@CrewBase
class ExpertAnalyst():
    """Expert Analyst crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True,
            llm=llm
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=True,
            tools=[TelegramNotificationTool()],
            llm=llm,
            allow_delegation=False,
            function_calling_llm=llm
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='output/report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Expert Analyst crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
