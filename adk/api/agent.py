# adk/api/agent.py
from types import SimpleNamespace
import os
import json
import re

class Agent:
    
    def __init__(self, config: dict):
      # pull fields out of the dict
       self.config = SimpleNamespace(**config)
       self.name          = self.config.name
       self.model         = self.config.model
       self.system_prompt = self.config.system_prompt
       self.tools         = self.config.tools
       #self.tools         = config.get("tools", [])
       # store any other config you need...
       
    def execute_tool(self, tool_name: str, *args, **kwargs):
        """Execute a tool by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                print(f"Executing tool: {tool_name}")
                result = tool.execute(*args, **kwargs)
                print(f"Tool result: {result}")
                return result
        return f"Tool '{tool_name}' not found"
    
    def parse_tool_calls(self, llm_response: str):
        """Parse LLM response for tool calls."""
        # Look for patterns like: tool_name(arg1, arg2) or tool_name(arg1="value1", arg2="value2")
        tool_calls = []
        
        # Pattern for function calls
        pattern = r'(\w+)\s*\(([^)]*)\)'
        matches = re.findall(pattern, llm_response)
        
        for tool_name, args_str in matches:
            # Parse arguments
            args = []
            kwargs = {}
            
            if args_str.strip():
                # Split by comma, but be careful about quoted strings
                arg_parts = []
                current_part = ""
                in_quotes = False
                quote_char = None
                
                for char in args_str:
                    if char in ['"', "'"] and not in_quotes:
                        in_quotes = True
                        quote_char = char
                        current_part += char
                    elif char == quote_char and in_quotes:
                        in_quotes = False
                        quote_char = None
                        current_part += char
                    elif char == ',' and not in_quotes:
                        arg_parts.append(current_part.strip())
                        current_part = ""
                    else:
                        current_part += char
                
                if current_part.strip():
                    arg_parts.append(current_part.strip())
                
                # Parse each argument
                for part in arg_parts:
                    part = part.strip()
                    if '=' in part and not part.startswith('"') and not part.startswith("'"):
                        # Keyword argument
                        key, value = part.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        kwargs[key] = value
                    else:
                        # Positional argument
                        # Remove quotes if present
                        if (part.startswith('"') and part.endswith('"')) or (part.startswith("'") and part.endswith("'")):
                            part = part[1:-1]
                        args.append(part)
            
            tool_calls.append({
                'tool_name': tool_name,
                'args': args,
                'kwargs': kwargs
            })
        
        return tool_calls
    
    def act(self, observation):
        # use self.config here if needed
        # For now, return a simple response object
        # In a real implementation, this would call the LLM and execute tools
        
        # Try to use OpenAI API if available
        try:
            import openai
            
            # Get API key from environment or config
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                # Try to get from config files
                try:
                    import yaml
                    with open("run_all_test.yaml", "r") as f:
                        config_data = yaml.safe_load(f)
                        api_key = config_data.get("openai_api_key")
                except:
                    pass
            
            if api_key:
                client = openai.OpenAI(api_key=api_key)
                
                # Prepare tools information for the LLM
                tools_info = ""
                if self.tools:
                    tools_info = "\n\nAvailable tools:\n"
                    for tool in self.tools:
                        tools_info += f"- {tool.name}: {tool.description}\n"
                        if tool.parameters:
                            tools_info += f"  Parameters: {tool.parameters}\n"
                
                # Enhanced system prompt with tool information
                enhanced_system_prompt = self.system_prompt + tools_info + "\n\nTo use a tool, write: tool_name(arg1, arg2, param1='value1')"
                
                # Prepare the message for the LLM
                messages = [
                    {"role": "system", "content": enhanced_system_prompt},
                    {"role": "user", "content": observation}
                ]
                
                # Call the LLM
                response = client.chat.completions.create(
                    model="gpt-4o",  # Use gpt-4o instead of gemini for now
                    messages=messages,
                    max_tokens=1000
                )
                
                llm_response = response.choices[0].message.content
                
                # Check for tool calls in the response
                tool_calls = self.parse_tool_calls(llm_response)
                
                if tool_calls:
                    # Execute tools and get results
                    tool_results = []
                    for tool_call in tool_calls:
                        result = self.execute_tool(
                            tool_call['tool_name'], 
                            *tool_call['args'], 
                            **tool_call['kwargs']
                        )
                        tool_results.append(f"{tool_call['tool_name']} result: {result}")
                    
                    # Send tool results back to LLM for final response
                    tool_results_text = "\n".join(tool_results)
                    messages.append({"role": "assistant", "content": llm_response})
                    messages.append({"role": "user", "content": f"Tool execution results:\n{tool_results_text}\n\nPlease provide a final response based on these results."})
                    
                    final_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        max_tokens=1000
                    )
                    
                    llm_response = final_response.choices[0].message.content
                
                # Create response object
                response_obj = SimpleNamespace()
                response_obj.agent_response = llm_response
                return response_obj
                
        except Exception as e:
            print(f"LLM call failed: {e}")
        
        # Fallback to simple response if LLM fails
        response = SimpleNamespace()
        response.agent_response = f"Agent {self.name} received: {observation}"
        return response
