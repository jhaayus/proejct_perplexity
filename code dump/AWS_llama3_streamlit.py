------------


----------- AWS GENAI -- workin gcode without S3 bucket storage 
import boto3
import json

def blog_gen_using_bedrock(blogtopic: str) -> str:
    prompt = f"<s>[INST]Human: Write 1 sentence on {blogtopic}[/INST]</s>"
    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.1,
        "top_p": 0.9
    }
    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId="meta.llama3-70b-instruct-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        response_content = response['body'].read().decode('utf-8')
        response_data = json.loads(response_content)
        blog_details = response_data.get('generation', 'No generation found')
        return blog_details
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Error"
        
def save_blog_details_s3(s3_key,s3_bucket,generate_blog):
    s3=boto3.client('s3')

    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body =generate_blog )
        print("Code saved to s3")

    except Exception as e:
        print("Error when saving the code to s3")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # Check if 'body' is in the event
        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps('Bad Request: Missing body in event')
            }

        # Parse the body
        try:
            event_body = json.loads(event['body'])
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {
                'statusCode': 400,
                'body': json.dumps('Bad Request: Invalid JSON format')
            }

        blogtopic = event_body.get('blog_topic', '')

        # Check if 'blog_topic' is present
        if not blogtopic:
            return {
                'statusCode': 400,
                'body': json.dumps('Bad Request: Missing blog_topic')
            }

        generate_blog = blog_gen_using_bedrock(blogtopic=blogtopic)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': generate_blog})
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal Server Error: {e}')
        }
        
        
        
        --------------------------------- working code 
        
        import boto3
import json
import datetime

def blog_gen_using_bedrock(blogtopic: str) -> str:
    prompt = f"<s>[INST]Human: Write 1 sentence on {blogtopic}[/INST]</s>"
    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.1,
        "top_p": 0.9
    }
    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId="meta.llama3-70b-instruct-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        response_content = response['body'].read().decode('utf-8')
        response_data = json.loads(response_content)
        blog_details = response_data.get('generation', 'No generation found')
        return blog_details
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Error"

def save_blog_details_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print("Blog saved to S3")
    except Exception as e:
        print(f"Error when saving blog to S3: {e}")

def lambda_handler(event, context):
    try:
        # Parse the incoming event
        event = json.loads(event['body'])
        blogtopic = event['blog_topic']

        # Generate the blog content
        generate_blog = blog_gen_using_bedrock(blogtopic=blogtopic)

        if generate_blog:
            # Save to S3
            current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            s3_key = f"blog-output/{current_time}.txt"
            s3_bucket = 'awsbedrockcoursejha'  
            save_blog_details_s3(s3_key, s3_bucket, generate_blog)
            print("Blog Generation is completed")
        else:
            print("No blog was generated")

        return {
            'statusCode': 200,
            'body': json.dumps('Blog Generation is completed')
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal Server Error: {e}')
        }
        
        
        
        ---------------------------------------- add funcationality to streamlit 
        
  