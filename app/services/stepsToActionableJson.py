import boto3, json, base64


class ActionableNodeConverter:
    
    MODEL_ARN = "arn:aws:bedrock:us-east-1:302511180962:inference-profile/global.anthropic.claude-opus-4-5-20251101-v1:0"
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.client = boto3.client("bedrock-runtime", region_name=region)
    
    def _load_json_file(self, file_path: str) -> dict:
        with open(file_path, "r") as f:
            return json.load(f)
    
    def _get_conversion_prompt(self, template_data: dict, nodes_data: dict) -> str:
        return f"""
You are an expert system architect. Convert the following IVR flowchart nodes into actionable JSON format.

TEMPLATE (use this structure for each node):
{json.dumps(template_data, indent=2)}

FLOWCHART NODES (convert these):
{json.dumps(nodes_data, indent=2)}

Instructions:
- For each node in the flowchart, create a JSON object following the template structure
- Populate each field using the information from the node
- If the node contains speech (description), put it inside params.audio.text
- If the node is a decision, set type to "agenticdecision"
- If it requires caller input, set type to "userInput"
- If it is a normal message or system-driven process, set type to "predefined"
- If the node has only one connection, set choice to "single", otherwise "multiple"
- Always include the node's actual id, name, and connections
- Always include actor from the node
- Always set command to "connect"
- If the action involves no audio prompt (e.g., API node), leave text as an empty string
- If there is no stopTime provided, use null
- Return an array of transformed nodes
- The JSON must be strictly valid

Output ONLY valid JSON with no markdown formatting, no code blocks, no explanations.
Start with [ and end with ]
"""
    
    def _clean_response(self, response_text: str) -> str:
        if response_text.startswith("```"):
            response_text = response_text.lstrip("`").lstrip("json").lstrip("\n")
            response_text = response_text.rstrip("`").rstrip("\n")
        return response_text
    
    def convert_nodes(self, nodes_file: str, template_file: str) -> dict:
        nodes_data = self._load_json_file(nodes_file)
        template_data = self._load_json_file(template_file)
        
        # Generate prompt
        prompt = self._get_conversion_prompt(template_data, nodes_data)
        
        # Prepare request body
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        }
        
        # Invoke the bedrock model
        response = self.client.invoke_model(
            modelId=self.MODEL_ARN,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )
        
        response_body = json.loads(response.get("body").read())
        result = response_body["content"][0]["text"]
        
        result = self._clean_response(result)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON. Error: {e}")
            print(f"Result content: {result[:500]}")
            raise
    
    def save_to_file(self, data: dict, output_file: str) -> None:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Actionable nodes saved to {output_file}")


if __name__ == "__main__":
    nodes_file = "../output_jsons/flowchart_nodes.json"
    template_file = "../utils/template.json"
    
    print(f"Loading nodes from {nodes_file}...")
    print(f"Loading template from {template_file}...")
    
    converter = ActionableNodeConverter()
    
    print("Converting nodes to actionable format...")
    actionable_nodes = converter.convert_nodes(nodes_file, template_file)
    
    output_file = "actionable_nodes.json"
    converter.save_to_file(actionable_nodes, output_file)
    
    
