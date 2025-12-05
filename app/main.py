"""
Main application file that orchestrates the flowchart processing pipeline.
Calls awsconnect.py to convert flowchart images to nodes,then stepsToActionableJson.py to convert nodes to actionable format.
"""

import sys
import json
import os
from pathlib import Path

os.chdir(Path(__file__).parent.parent)

from services.awsconnect import FlowchartProcessor
from services.stepsToActionableJson import ActionableNodeConverter


class FlowchartPipeline:
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.processor = FlowchartProcessor(region=region)
        self.converter = ActionableNodeConverter(region=region)
    
    def process_flowchart(self, image_path: str, output_nodes_file: str = "flowchart_nodes.json",
                          output_actionable_file: str = "actionable_nodes.json", 
                          template_file: str = "template.json") -> dict:
        print(f"\nConverting flowchart image to nodes...")
        print(f"  Input: {image_path}")
        nodes_data = self.processor.image_to_nodes(image_path)
        self.processor.save_nodes_to_file(nodes_data, output_nodes_file)
        print(f"  Template: {template_file}")
        actionable_nodes = self.converter.convert_nodes(output_nodes_file, template_file)
        self.converter.save_to_file(actionable_nodes, output_actionable_file)
        
        print(f"  Generated files:")
        print(f"    1. {output_nodes_file}")
        print(f"    2. {output_actionable_file}")
        print("=" * 60 + "\n")
        
        return actionable_nodes
    
    def process_flowchart_to_nodes_only(self, image_path: str, 
                                        output_file: str = "flowchart_nodes.json") -> dict:
       
        print(f"Converting flowchart image to nodes...")
        nodes_data = self.processor.image_to_nodes(image_path)
        self.processor.save_nodes_to_file(nodes_data, output_file)
        return nodes_data
    
    def process_nodes_to_actionable_only(self, nodes_file: str, template_file: str,
                                         output_file: str = "actionable_nodes.json") -> dict:
        """
        Process only the second step: Convert nodes to actionable format.
        
        Args:
            nodes_file: Path to the nodes JSON file
            template_file: Path to the template JSON file
            output_file: Output file for actionable nodes
            
        Returns:
            Dictionary containing the actionable nodes
        """
        print(f"Converting nodes to actionable JSON format...")
        actionable_nodes = self.converter.convert_nodes(nodes_file, template_file)
        self.converter.save_to_file(actionable_nodes, output_file)
        return actionable_nodes


def main():
    try:
        pipeline = FlowchartPipeline()
        
        print("Running complete flowchart processing pipeline...\n")
        final_result = pipeline.process_flowchart(
            image_path="data/flowchart.png",
            output_nodes_file="output_jsons/flowchart_nodes.json",
            output_actionable_file="output_jsons/actionable_nodes.json",
            template_file="template.json"
        )
        
        print("Preview of actionable nodes:")
        if isinstance(final_result, list):
            print(json.dumps(final_result[:1], indent=2))  # Print first node as preview
        else:
            print(json.dumps(final_result, indent=2)[:500])
        
        return final_result
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        print("Make sure all required files exist:")
        print("  - data/flowchart.png (input image)")
        print("  - template.json (template file)")
        return None
    except Exception as e:
        print(f"Error processing flowchart: {e}")
        raise


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
