import os
import yaml
import glob
from datetime import datetime

# Replace 'path/to/namespaces' with the actual path to the parent directory containing namespaces
namespaces_dir = 'must-gather.local.3258111095487292326/docker-io-puneet2147-must-gather-sha256-74abd480202877741e8d221fec6fbe27a179b45d2ab2edc6b6fdf9b49d166d7c/namespaces'

# -----------------------------------------------------------------------------
def process_pipeline_runs(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        yaml_data = file.read()

    data = yaml.safe_load(yaml_data)

    taskrun_info = []
    if 'status' in data and 'childReferences' in data['status']:
        for taskrun in data['status']['childReferences']:
            if 'name' in taskrun:
                taskrun_info.append({
                    'name': taskrun['name'],
                    'namespace': data['metadata']['namespace']
                })

    return taskrun_info, data['metadata']['creationTimestamp'], data.get('status', {}).get('startTime', 'N/A'), data.get('status', {}).get('completionTime', 'N/A')

# -----------------------------------------------------------------------------
def process_task_runs(namespace_dir, yaml_file_path, pr_creation_time):
    with open(yaml_file_path, 'r') as file:
        yaml_data = file.read()

    data = yaml.safe_load(yaml_data)
    taskrun_info = []
    taskrunCreationTimeToStartTime = calculatePipelineRunDuration(data['metadata']['creationTimestamp'], data.get('status', {}).get('startTime', 'N/A'))
    prCreationTimeToTaskRunStartTime = calculatePipelineRunDuration(pr_creation_time, data.get('status', {}).get('startTime', 'N/A'))

    taskrun_info.append({
        'startTime': data.get('status', {}).get('startTime', 'N/A'),
        'creationTime': data['metadata']['creationTimestamp'],
        'completionTime': data.get('status', {}).get('completionTime', 'N/A'),
        'taskrunCreationTimeToStartTime': taskrunCreationTimeToStartTime,
        'pipelineRunCreationTimeToTaskRunStartTime': prCreationTimeToTaskRunStartTime,
        'lastTransitionTime': data['status']['conditions'][0]['lastTransitionTime'],
        'PodInfo': []
    })

    tr_creation_time = data['metadata']['creationTimestamp']

    # Get the pod details
    # Define the custom order index for each type
    order_index = {
        'PodScheduled': 0,
        'Initialized': 1,
        'ContainersReady': 2,
        'Ready': 3
    }

    pod_dir = os.path.join(namespace_dir, 'pods')
    pod_path = os.path.join(pod_dir, data.get('status', {}).get('podName', 'N/A'))

    pod_info = []
    yaml_files = glob.glob(os.path.join(pod_path, '*.yaml'))
    for yaml_file in yaml_files:
        with open(yaml_file, 'r') as file:
            pod_yaml_data = file.read()

        pod_data = yaml.safe_load(pod_yaml_data)
        conditions = pod_data['status']['conditions']
        sorted_conditions = sorted(conditions, key=lambda x: order_index.get(x.get('type', 'N/A'), float('inf')))

        taskRunCreationTimeToPodCreationTime = calculatePipelineRunDuration(tr_creation_time, pod_data['metadata']['creationTimestamp'])

        taskrun_info[-1]['PodInfo'].append({
            'name': data.get('status', {}).get('podName', 'N/A'),
            'creationTime': pod_data['metadata']['creationTimestamp'],
            'trToPod': taskRunCreationTimeToPodCreationTime,
        }
                                             )
        for condition in sorted_conditions:
            last_transition_time = condition.get('lastTransitionTime', 'N/A')
            condition_type = condition.get('type', 'N/A')

            pod_info.append({
                'lastTransitionTime': {last_transition_time},
                'conditionType': {condition_type}
            })

    return taskrun_info, pod_info

# -----------------------------------------------------------------------------
def calculatePipelineRunDuration(t1, t2):
    # Convert the timestamps to datetime objects
    dt1 = datetime.fromisoformat(t1.replace("Z", "+00:00"))
    dt2 = datetime.fromisoformat(t2.replace("Z", "+00:00"))

    # Calculate the time difference
    time_difference = dt2 - dt1

    # Get the time difference in seconds
    time_difference_seconds = time_difference.total_seconds()
    return time_difference_seconds

# -----------------------------------------------------------------------------
def main():
    resource_info = []
    # Traverse through namespaces directory
    for namespace_name in os.listdir(namespaces_dir):
        namespace_dir = os.path.join(namespaces_dir, namespace_name)

        # Check if it is a directory
        if os.path.isdir(namespace_dir):
            # Traverse through pipelineRun directory within the namespace
            pipeline_run_dir = os.path.join(namespace_dir, 'pipelinerun')
            task_run_dir = os.path.join(namespace_dir, 'taskrun')
            pod_dir = os.path.join(namespace_dir, 'pods')
            if os.path.isdir(pipeline_run_dir):
                # Filter out only directories within pipeline_run_dir
                pipeline_run_names = [dir_name for dir_name in os.listdir(pipeline_run_dir) if os.path.isdir(os.path.join(pipeline_run_dir, dir_name))]

                # Traverse through each pipeline_run_name directory
                for pipeline_run_name in pipeline_run_names:
                    pipeline_run_path = os.path.join(pipeline_run_dir, pipeline_run_name)
                    # Find YAML files in the pipeline_run_name directory
                    yaml_files = glob.glob(os.path.join(pipeline_run_path, '*.yaml'))
                    for yaml_file in yaml_files:
                        # Call process_pipeline_runs function for each YAML file
                        taskrun_info, pr_creation_time, pr_start_time, pr_completion_time = process_pipeline_runs(yaml_file)

                        prDuration = calculatePipelineRunDuration(pr_creation_time, pr_completion_time)
                        prCreationTimeToStartTime = calculatePipelineRunDuration(pr_creation_time, pr_start_time)

                        resource_info.append({
                            'name': pipeline_run_name,
                            'namespace': namespace_name,
                            'creationTime': pr_creation_time,
                            'startTime': pr_start_time,
                            'completionTime': pr_completion_time,
                            'pipelineRunCreationTimeToStartTime': prCreationTimeToStartTime,
                            'pipelineRunDuration': prDuration,
                            'taskruns': []
                        })

                        for info in taskrun_info:
                            task_run_path = os.path.join(task_run_dir, info['name'])
                            yaml_files = glob.glob(os.path.join(task_run_path, '*.yaml'))
                            for yaml_file in yaml_files:
                                task_run_info, pod_info = process_task_runs(namespace_dir, yaml_file, pr_creation_time)
                                resource_info[-1]['taskruns'].append({
                                    'TaskRunName': info['name'],
                                    'Namespace': info['namespace'],
                                    'TaskRunInfo': task_run_info,
                                    'Pods': pod_info,
                                })

    sorted_resource_info_descending = sorted(resource_info, key=lambda x: x['pipelineRunDuration'], reverse=True)

    # Print the sorted array in descending order
    for item in sorted_resource_info_descending:
        print()
        print("PipelineRunName ----->", item['name'])
        print("Namespace ------------->", item['namespace'])
        print("PipelineRun Duration ----->", item['pipelineRunDuration'])
        print("Pipeline Run Creation Time To Start Time --->", item['pipelineRunCreationTimeToStartTime'])
        print()
        for taskrun in item['taskruns']:
            taskrun_name = taskrun['TaskRunName']
            for task_info in taskrun['TaskRunInfo']:
                taskrun_creation_time_to_start_time = task_info['taskrunCreationTimeToStartTime']
                pr_creation_time_to_tr_start_time = task_info['pipelineRunCreationTimeToTaskRunStartTime']
                pod_info = task_info['PodInfo'][0]
                tr_to_pod = pod_info['trToPod']

                print(f"TaskRunName -----> {taskrun_name}")
                print(f"Task Run Creation Time To StartTime -----> {taskrun_creation_time_to_start_time}")
                print(f"TaskRun Creation Time To Pod Creation Time-----> {tr_to_pod}")
                print(f"PR Creation Time to TR Creation Time ---> {pr_creation_time_to_tr_start_time}")
                print()

        print("=================================================================")

if __name__ == "__main__":
    main()
