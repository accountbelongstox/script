<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
class TaskHandler
{
    private $taskDir = null;
    private $taskFile = null;
    private $task_object = array(
        'task' => array(
            'file' => null,
            'list' => [],
            'task_key' => null,
            'task_name' => null,
        ),
        'done' => array(
            'file' => null,
            'list' => [],
            'task_key' => null,
            'task_name' => null,
        ),
    );
    private $jsonFiles = [];
    public function __construct()
    {
        $action = $_REQUEST['action'] ?? '';
        $task_name = $_REQUEST['task_name'] ?? '';
        $namespace = $_REQUEST['namespace'] ?? '';
        if (empty($action) || empty($task_name) || empty($namespace)) {
            $this->jsonResponse("action, task_name, namespace cannot be empty. 
            action:[query | put | complete], 
            task_name:[task-identifier]
            namespace:[default or a name]");
            die;
        }
    }

    public function getTaskDir($fix_name=null,$task_name = null)
    {
        $taskName = $task_name ?? ($_REQUEST['task_name'] ?? 'default');
        $namespace = $this->getNameSpace();
		if ($fix_name !== null){
			$fix_name = "/" . $fix_name;
		}else{
			$fix_name = "";
		}
        $taskDir = ".tasks/" . $taskName . "/" . $namespace . $fix_name;
        if (!file_exists($taskDir)) {
            mkdir($taskDir, 0777, true);
        }
        return $taskDir;
    }

	public function getDoneFile($doneFile)
    {
		$doneDir = $this->getTaskDir('done');
        $file = $doneDir . "/" . $doneFile;
        return $file;
    }

    public function initTask($taskName = "task", $ext = "json")
    {
        $file = $this->getJsonFile($taskName . "." . $ext);
        $this->task_object[$taskName]["file"] = $file;
        if (file_exists($file)) {
            $this->task_object[$taskName]["list"] = json_decode(file_get_contents($file), true);
        }
        // else {
        //     file_put_contents($this->jsonFiles[$taskObject], json_encode($this->taskObjects[$taskObject]['list']));
        // }
    }

    public function getJsonFile($jsonFile = "task.json")
    {
		$dir = $this->getTaskDir();
        $file = $dir . "/" . $jsonFile;
        return $file;
    }

    public function getNameSpace($namespace = null)
    {
        $namespace = $namespace ?? ($_REQUEST['namespace'] ?? 'default');
        return $namespace;
    }

    public function jsonResponse($data)
    {
        if (is_string($data)) {
            $data = ['message' => $data];
        }
        echo json_encode($data);
    }

	public function taskRequest()
	{
		$action = $_REQUEST['action'] ?? '';
		if ($action === 'add') {
			$this->addTask();
		} elseif ($action === 'complete') {
			$this->completeTask();
		} elseif ($action === 'get_tasks') {
			$this->getTaskList();
		} elseif ($action === 'get_done') {
			$this->getComplete();
		} else {
			$this->jsonResponse(['status' => 'error', 'message' => 'Invalid action']);
		}
	}

	public function getTaskList()
	{
		$taskName = "task";
		$this->initTask($taskName,"json");
		$this->jsonResponse(['status' => 'success', 'task' => $this->task_object[$taskName]]);
	}

    private function addTask()
    {
		$taskName = "task";
		$this->initTask($taskName,"json");
        $namespace = $this->getNameSpace();
        $name = $_REQUEST['name'] ?? '';
        $taskContent = $_REQUEST['task_content'] ?? '';
        $taskKey = md5($taskContent);
        $id = $_REQUEST['id'] ?? $taskKey;
        $task_path = $_REQUEST['task_path'] ?? $namespace;
        $this->task_object[$taskName]["list"][$taskKey] = [
            "namespace" => $namespace,
            "name" => $name,
            "task_path" => $task_path,
             
            "id" => $id,
            "task_content" => $taskContent,
            "complete_content" => '',
            "done" => false,
            "complete_path" => null,
            "result" => null,
            "submit_time" => time(),
            "completion_time" => null,
        ];
        $task_list = $this->task_object[$taskName]["list"];
        $task_file = $this->task_object[$taskName]["file"];
        file_put_contents($task_file, json_encode($task_list, JSON_PRETTY_PRINT));
        $this->jsonResponse(['status' => 'success', 'message' => 'Task added successfully, Current Task length '. count($this->task_object[$taskName]["list"]) ]);
    }

	private function deleteTaskById($id)
	{
		$taskName = "task";
		$this->initTask($taskName,"json");
		$taskList = &$this->task_object[$taskName]["list"];
		if (isset($taskList[$id])) {
			$deletedTask = $taskList[$id];
			unset($taskList[$id]);
			$taskFile = $this->task_object[$taskName]["file"];
			file_put_contents($taskFile, json_encode($taskList, JSON_PRETTY_PRINT));
			$this->jsonResponse([
				'status' => 'success',
				'message' => 'Task deleted successfully',
				'task_entity' => $deletedTask,
				'current_task_length' => count($taskList)
			]);
		} else {
			$this->jsonResponse(['status' => 'error', 'message' => 'Task not found for the provided ID.']);
		}
	}

    public function getTaskById($taskId, $taskName = "task")
    {
        $this->initTask($taskName, "json");
        if (isset($this->task_object[$taskName]["list"][$taskId])) {
            return $this->task_object[$taskName]["list"][$taskId];
        } else {
            return null;
        }
    }

	private function getComplete()
	{
        $taskContent = $_REQUEST['task_content'] ?? null;
        $taskKey = md5($taskContent);
		$id = $_REQUEST['id'] ?? $taskKey;
		if ($id === null) {
			return $this->jsonResponse(['status' => 'error', 'message' => 'task_content and ID are required..']);
		}
		$taskEntity = $this->getCompleteTaskById($id);
		$completeContent = $this->getCompleteContentById($id);
		return $this->jsonResponse(['status' => 'success', 'task_entity' => $taskEntity, 'complete_content' => $completeContent]);
	}

	private function getCompleteTaskById($id)
	{
		$completePath = $this->getDoneFile($id . ".json");
		if (!file_exists($completePath)) {
			return null;
		}
		return json_decode(file_get_contents($completePath), true);
	}

	private function getCompleteContentById($id)
	{
		$completePath = $this->getDoneFile($id . ".txt");
		if (!file_exists($completePath)) {
			return null;
		}
		return file_get_contents($completePath);
	}

	private function updateTaskStatus($id, $done, $resultPath, $completeContent)
	{
		$taskName = "task";
        $this->initTask($taskName, "json");
		$taskList = &$this->task_object[$taskName]["list"];
		if (isset($taskList[$id])) {
			$task = &$taskList[$id];
			$task["done"] = $done;
			$task["completion_time"] = time();
			$task["result"] = $resultPath;
			$task["complete_path"] = $this->getDoneFile($id . ".txt");
			if (!empty($completeContent)) {
				file_put_contents($task["complete_path"], $completeContent);
			}
			$taskFile = $this->task_object[$taskName]["file"];
			file_put_contents($taskFile, json_encode($taskList, JSON_PRETTY_PRINT));
			return true;
		}
		return false;
	}

	private function completeTask()
	{
		$taskName = "done";
		$this->initTask($taskName, "json");
		$namespace = $this->getNameSpace();
		$completeContent = $_REQUEST['complete_content'];
		$id = $_REQUEST['id'];
		if (empty($completeContent) || empty($id)) {
			$this->jsonResponse(['status' => 'error', 'message' => 'Complete content and ID are required.']);
			return;
		}
		$taskEntity = $this->getTaskById($id);
		if ($taskEntity === null) {
			$this->jsonResponse(['status' => 'error', 'message' => 'Task not found for the provided ID.']);
			return;
		}
		$completePath = $this->getDoneFile($id . ".txt");
		$completeJsonPath = $this->getDoneFile($id . ".json");
		$updatedTaskEntity = [
			"namespace" => $taskEntity["namespace"],
			"name" => $taskEntity["name"],
			"task_path" => $taskEntity["task_path"],
			"task_content" => $taskEntity["task_content"],
			"complete_content" => $completeContent,
			"done" => true,
			"submit_time" => time(),
			"completion_time" => time(),
			"result" => $completeJsonPath,
			"complete_path" => $completePath,
		];
		file_put_contents($completeJsonPath, json_encode($updatedTaskEntity, JSON_PRETTY_PRINT));
		file_put_contents($completePath, $completeContent);
		$updatedTaskEntity["complete_path"] = $completePath;
		$this->task_object[$taskName]["list"][$id] = $updatedTaskEntity;
		$taskList = $this->task_object[$taskName]["list"];
		$taskFile = $this->task_object[$taskName]["file"];
		file_put_contents($taskFile, json_encode($taskList, JSON_PRETTY_PRINT));
		$this->updateTaskStatus($id, true, $completePath, $completeContent);
		$this->jsonResponse(['status' => 'success', 'message' => 'Task completed successfully', 'list_length' => count($taskList)]);
	}
}

$taskHandler = new TaskHandler();
$taskHandler->taskRequest();

?>