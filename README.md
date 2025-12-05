# auflowtojson
This repo converts the visual flow into set of nodes as steps then to a predefined json template.

Step 1: Install required libraries and configure AWS bedrock models. In case if you're using other models other than claude, please get it from the model inference page by copying it's ARN.
Step 2: main.py - run it and the images are already present in the form of png. However, you can replace it with your own flowchart image.
Step 3: After running main.py, it will generate the actionable json file out of the flow.

Pending:
1. Validation
2. Test classes
3. Need to try with complex flows
4. JSON file can be fixed to AWS connect expected format or can add aditional layer to convert or we can add these things in the prompt to give it in AWS connect format.
