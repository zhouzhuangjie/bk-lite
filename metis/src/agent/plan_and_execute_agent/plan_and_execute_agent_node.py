import json
from typing import List, Union

from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from src.agent.plan_and_execute_agent.plan_and_execute_agent_state import PlanAndExecuteAgentState
from src.core.node.tools_node import ToolsNodes
from loguru import logger


class Plan(BaseModel):
    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )


class Response(BaseModel):
    response: str


class Act(BaseModel):
    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
                    "If you need to further use tools to get the answer, use Plan."
    )


class PlanAndExecuteAgentNode(ToolsNodes):
    async def execute_step(self, state: PlanAndExecuteAgentState, config: RunnableConfig):
        plan = state["plan"]
        plan_str = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(plan))
        task = plan[0]

        llm = self.get_llm_client(config["configurable"]["graph_request"])
        agent_executor = create_react_agent(llm, self.tools,
                                            prompt=config["configurable"]["graph_request"].system_message_prompt)

        task_formatted = f"""For the following plan:
    {plan_str}\n\nYou are tasked with executing step {1}, {task}."""
        logger.info(task_formatted)
        agent_response = await agent_executor.ainvoke(
            {"messages": [("user", task_formatted)]}
        )
        return {
            "past_steps": [(task, agent_response["messages"][-1].content)],
        }

    def should_end(self, state: PlanAndExecuteAgentState):
        if "response" in state and state["response"]:
            return END
        else:
            return "agent"

    async def replan_step(self, state: PlanAndExecuteAgentState, config: RunnableConfig):
        prompt = f"""For the given objective, come up with a simple step by step plan. Here is tools you can use {self.tools}
                    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps.
                    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
                    Your objective was this:
                    {config["configurable"]['graph_request'].user_message}

                    Your original plan was this:
                    {state['plan']}

                    You have currently done the follow steps:
                    {state['past_steps']}

                    Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that.
                    Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. 
                    Do not return previously done steps as part of the plan.
        """
        replanner_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt,),
                ("placeholder", "{messages}"),
            ]
        )
        llm = self.get_llm_client(config["configurable"]["graph_request"])
        replanner = replanner_prompt | llm.with_structured_output(Act)
        output = await replanner.ainvoke({"messages": [
            ("user", config["configurable"]['graph_request'].user_message)
        ]})

        logger.debug(f"重规划的步骤:{output}")

        if isinstance(output.action, Response):
            return {"response": output.action.response}
        else:
            return {"plan": output.action.steps}

    async def plan_step(self, state: PlanAndExecuteAgentState, config: RunnableConfig):
        prompt = f"""
            For the given objective, come up with a simple step by step plan. Here is tools you can use {self.tools}
            This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps.
            The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
            use json format for the output,  a list of strings as the value.
"""
        planner_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt,),
                ("placeholder", "{messages}"),
            ]
        )

        llm = self.get_llm_client(config["configurable"]["graph_request"])

        planner = planner_prompt | llm.with_structured_output(Plan)

        plan = await planner.ainvoke({"messages": [
            ("user", config["configurable"]['graph_request'].user_message)
        ]})

        logger.debug(f"规划的步骤:{plan}")
        return {"plan": plan.steps}
