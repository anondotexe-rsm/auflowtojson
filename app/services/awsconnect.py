import boto3, json, base64


class FlowchartProcessor:
    """
    A class to process flowchart images and convert them to structured node JSON format
    using AWS Bedrock and Claude AI.
    """
    
    MODEL_ARN = "arn:aws:bedrock:us-east-1:302511180962:inference-profile/global.anthropic.claude-opus-4-5-20251101-v1:0"
    
    def __init__(self, region: str = "us-east-1"):
        """
        Initialize the FlowchartProcessor.
        
        Args:
            region: AWS region for Bedrock client (default: us-east-1)
        """
        self.region = region
        self.client = boto3.client("bedrock-runtime", region_name=region)
    
    def _load_image_as_base64(self, image_path: str) -> str:
        """
        Load an image file and convert it to base64 encoding.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string of the image
        """
        with open(image_path, "rb") as f:
            img_bytes = f.read()
            return base64.b64encode(img_bytes).decode("utf-8")
    
    def _get_prompt(self) -> str:
        """
        Get the prompt template for converting flowchart images to structured nodes.
        
        Returns:
            Prompt string for the LLM
        """
        return """
You are an expert system architect.

Read the flowchart in the image and convert it into structured nodes.

Each node must contain:
- id
- name
- type (start, process, decision, api, end)
- description
- connections (array of node ids)
- actor (caller, agent, system)

Output ONLY valid JSON with no markdown formatting, no code blocks, no explanations, no additional text.
Start your response with { and end with }
"""
    
    def _clean_response(self, response_text: str) -> str:
        """
        Clean up the API response by removing markdown formatting if present.
        
        Args:
            response_text: Raw response text from the API
            
        Returns:
            Cleaned response text
        """
        if response_text.startswith("```"):
            response_text = response_text.lstrip("`").lstrip("json").lstrip("\n")
            response_text = response_text.rstrip("`").rstrip("\n")
        return response_text
    
    def image_to_nodes(self, image_path: str) -> dict:
        """
        Convert a flowchart image to structured node data using Claude AI.
        
        Args:
            image_path: Path to the flowchart image file
            
        Returns:
            Dictionary containing the structured nodes
            
        Raises:
            JSONDecodeError: If the response cannot be parsed as JSON
        """
        # Convert image to base64
        img_base64 = self._load_image_as_base64(image_path)
        prompt = self._get_prompt()
        
        # Prepare the request body
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_base64
                            }
                        }
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
            raise
    
    def save_nodes_to_file(self, nodes: dict, output_file: str) -> None:
        """
        Save the processed nodes to a JSON file.
        
        Args:
            nodes: Dictionary containing the nodes data
            output_file: Path to the output JSON file
        """
        with open(output_file, "w") as f:
            json.dump(nodes, f, indent=2)
        print(f"Flowchart nodes saved to {output_file}")


if __name__ == "__main__":
    processor = FlowchartProcessor()
    
    nodes = processor.image_to_nodes("flowchart.png")
    
    output_file = "../output_jsons/flowchart_nodes.json"
    processor.save_nodes_to_file(nodes, output_file)
    
    print(json.dumps(nodes, indent=2))
