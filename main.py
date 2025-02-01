import requests
import json
# Constants for GPT-4 API
openai_api_key = ''
model = 'gpt-4o'

# API URL and Headers
url = 'https://api.openai.com/v1/chat/completions'
headers = {
    'Authorization': 'Bearer ' + openai_api_key,
    'Content-Type': 'application/json',
}

# Global state that stores outputs from each agent
global_context = {
    "code_context": "",             # Stores the context of the code
    "code_context_verifier": "",             # Stores the context of the code
    "analysis_report": "",          # Stores the analysis report
    "analysis_report_verifier": "",          # Stores the analysis report
    "refactoring_strategy": "",     # Stores the refactoring strategy
    "refactoring_strategy_verifier": "",     # Stores the refactoring strategy
    "refactored_code": "",          # Stores the refactored code
    "refactored_code_report": "",          # Stores the refactored code Report
    "test_suite": "",               # Stores the test suite
}


def call_agent(agent_file, input_data, task_type):
    with open(agent_file, 'r') as file:
        agent_prompt = file.read()
    
    # payload = {
    #     'model': model,
    #     'messages': [{'role': 'system', 'content': agent_prompt+ f"\n\n{task_type} Input:\n" + input_data}]
    # }

    payload = {
        'model': model,
        'messages': [{'role': 'system', 'content': agent_prompt+ f"\n\n{task_type}"}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    return response.json()['choices'][0]['message']['content']

def multi_agent_team_refactor(haskell_code):
    agents_dir = "agents/"
    
    try:
        # Step 1: Code Context Agent
        # Send both the original code and the input data (which is initially just the code)
        code_and_context_input = f"Haskell Code:\n{haskell_code}"
        global_context["code_context"] = call_agent(agents_dir + "code_context_agent.txt", code_and_context_input, "Code Context")
        print(f"Code Context Report:\n{global_context['code_context']}\n")
        verified_context_input = f"Haskell Code:\n{haskell_code}\n\nContext Summary:\n{global_context['code_context']}"
        global_context["code_context_verifier"] = call_agent(agents_dir + "code_context_verifier_agent.txt", verified_context_input, "Code Context Verification")
        print(f"Verified Code Context Report:\n{global_context['code_context_verifier']}\n")

        # Step 2: Code Analysis Agent
        # Pass both the original code and the verified context summary
        code_and_analysis_input = f"Haskell Code:\n{haskell_code}\n\nContext Summary:\n{global_context['code_context']}\n\nVerified Context:\n{global_context['code_context']}"
        global_context["analysis_report"] = call_agent(agents_dir + "code_analysis_agent.txt", code_and_analysis_input, "Code Analysis")
        print(f"Code Analysis Report:\n{global_context['analysis_report']}\n")
        verified_analysis_input = f"Haskell Code:\n{haskell_code}\n\nAnalysis Report:\n{global_context['analysis_report']}"
        global_context["analysis_report_verifier"] = call_agent(agents_dir + "analysis_verifier_agent.txt", verified_analysis_input, "Code Analysis Verification")
        print(f"Verified Code Analysis Report:\n{global_context['analysis_report_verifier']}\n")

        # Step 3: Refactoring Strategy Agent
        # Pass both the original code and the verified analysis report
        code_and_strategy_input = f"Haskell Code:\n{haskell_code}\n\nAnalysis Report:\n{global_context['analysis_report']}\n\nVerified Analysis:\n{global_context['analysis_report']}"
        global_context["refactoring_strategy"] = call_agent(agents_dir + "refactoring_strategy_agent.txt", code_and_strategy_input, "Refactoring Strategy")
        print(f"Code Refactoring Strategy Report:\n{global_context['refactoring_strategy']}\n")
        verified_strategy_input = f"Haskell Code:\n{haskell_code}\n\nRefactoring Strategy:\n{global_context['refactoring_strategy']}"
        global_context["refactoring_strategy_verifier"] = call_agent(agents_dir + "refactoring_strategy_verifier_agent.txt", verified_strategy_input, "Refactoring Strategy Verification")
        print(f"Verified Code Refactoring Strategy Report:\n{global_context['refactoring_strategy_verifier']}\n")

        # Step 4: Code Refactoring Agent
        # Pass both the original code and the verified refactoring strategy
        code_and_refactor_input = f"Haskell Code:\n{haskell_code}\n\nRefactoring Strategy:\n{global_context['refactoring_strategy']}\n\nVerified Refactoring Strategy:\n{global_context['refactoring_strategy']}"
        # code_and_refactor_input = f"Original Code:\n{haskell_code}"
        refactored_code_result = call_agent(agents_dir + "refactor_code_agent.txt", code_and_refactor_input, "Code Refactoring")
        global_context["refactored_code_report"] = refactored_code_result

        print(f"Refactor Code Report:\n{global_context['refactored_code_report']}\n")

        if "```haskell" in refactored_code_result:
            only_refactored_code = refactored_code_result.split("```haskell")[-1].split("```")[0]
            # print(f"Only Refactor Code:\n{only_refactored_code}\n")
            global_context["refactored_code"] = only_refactored_code
        else:
            global_context["refactored_code"] = refactored_code_result
        

        
        print(f"Refactor Code:\n{global_context['refactored_code']}\n")

        verified_refactored_input = f"Haskell Code:\n{haskell_code}\n\nRefactored Code:\n{global_context['refactored_code']}"
        verified_refactored_code_result = call_agent(agents_dir + "refactored_code_verifier.txt", verified_refactored_input, "Refactored code Verification")
        global_context['refactored_code_report'] = verified_refactored_code_result
        print(f"Verified refactored Code Report :\n{global_context['refactored_code_report']}\n")

        # if "```haskell" in verified_refactored_code_result:
        #     only_refactored_code = verified_refactored_code_result.split("```haskell")[1].split("```")[0]
        #     # print(f"Only Refactor Code:\n{only_refactored_code}\n")
        #     global_context["refactored_code"] = only_refactored_code

        # print(f"Verified refactored Code:\n{global_context['refactored_code']}\n")

        
        
        # Step 5: Testing and Validation Agent
        # Pass both the refactored code and the original code
        code_and_test_input = f"Refactored Code:\n{global_context['refactored_code']}"
        testing_result= call_agent(agents_dir + "testing_validation_agent.txt", code_and_test_input, "Testing and Validation")
        print(f"Test Code:\n{testing_result}\n")

        # Step 6: Debugging Loop if Tests Fail
        while "fail" in testing_result.lower():
            debug_agent_input = f"Testing and Validation:\n{testing_result}\n\nRefactored Code:\n{global_context['refactored_code']}"
            debugged_code = call_agent(agents_dir + "debug_agent.txt", debug_agent_input, "Debug")

            # if "```haskell" in debugged_code:
            #     only_refactored_code = debugged_code.split("```haskell")[1].split("```")[0]
            #     # print(f"Only Refactor Code:\n{only_refactored_code}\n")
            #     global_context["refactored_code"] = only_refactored_code

            print(f"Debugged Report:\n{debugged_code}\n")

            testing_validation_prompt = f"Re-test the following debugged code:\n{global_context["refactored_code"]}"
            testing_result = call_agent(agents_dir + "testing_validation_agent.txt", testing_validation_prompt, "Testing and Validation")
            print(f"Test Code:\n{testing_result}\n")
        
        global_context["test_suite"] = testing_result

        # Save the refactored code
        with open('out/refactored_codebases.hs', 'w') as file:
            file.write(global_context["refactored_code"])

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    return True

if __name__ == "__main__":
    # Load the Haskell code
    with open("codebase.hs", "r") as file:
        haskell_code = file.read()

    # print(f"org code: {haskell_code}")
    # code_and_refactor_input = f"Original Code:\n{haskell_code}"
    # refactored_code_result = call_agent("agents/refactor_code_agent.txt", code_and_refactor_input, "Code Refactoring")

    # print(f"Refactor Code Report:\n{refactored_code_result}\n")

    # if "```haskell" in refactored_code_result:
    #     only_refactored_code = refactored_code_result.split("```haskell")[1].split("```")[0]
    #     print(f"Only Refactor Code:\n{only_refactored_code}\n")
    # Run the multi-agent refactoring process
    success = multi_agent_team_refactor(haskell_code)
    if success:
        print("Refactoring completed successfully!")
    else:
        print("Refactoring failed. Check the logs for details.")

