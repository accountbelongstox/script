<?php

namespace App\Http\Controllers;
use Carbon\Carbon;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class TaskController extends Controller
{
	private $requiredParams = ['action', 'task_name', 'namespace'];

    private $task_object = [
        'task' => [
            'file' => null,
            'list' => [],
            'task_key' => null,
            'task_name' => null,
        ],
        'done' => [
            'file' => null,
            'list' => [],
            'task_key' => null,
            'task_name' => null,
        ],
    ];

    public function __construct(Request $request)
    {

    }

	public function getTaskDir($fix_name = null, $task_name = null)
	{
		$taskName = $task_name ?? request('task_name', 'default');
		$namespace = $this->getNameSpace();
		if ($fix_name !== null) {
			$fix_name = "/" . $fix_name;
		} else {
			$fix_name = "";
		}
		$taskDir = ".tasks/" . $taskName . "/" . $namespace . $fix_name;
		Storage::makeDirectory($taskDir);
		#$taskDirPath = storage_path($taskDir);
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
		if (Storage::exists($file)) {
			$this->task_object[$taskName]["list"] = json_decode(Storage::get($file), true);
		}
	}

    public function getJsonFile($jsonFile = "task.json")
    {
        $dir = $this->getTaskDir();
        $file = $dir . "/" . $jsonFile;
        return $file;
    }

    public function getNameSpace($namespace = null)
    {
        $namespace = $namespace ?? request('namespace', 'default');
        return $namespace;
    }

    public function jsonResponse($data)
    {
        if (is_string($data)) {
            $data = ['message' => $data];
        }

        return response()->json($data);
    }

    public function taskRequest(Request $request)
    {

		$action = $request->input('action', '');
        $task_name = $request->input('task_name', '');
        $namespace = $request->input('namespace', '');
        if (empty($action) || empty($task_name) || empty($namespace)) {
            return response()->json([
                'status' => 'error',
                'message' => 'action, task_name, namespace cannot be empty. action:[query | put | complete | get_tasks | get_done], task_name:[task-identifier]namespace:[default or a name]'
            ]);
        }

        if ($action === 'add') {
            return $this->addTask($request);
        } elseif ($action === 'complete') {
            return $this->completeTask($request);
        } elseif ($action === 'get_tasks') {
            return $this->getTaskList();
        } elseif ($action === 'get_done') {
            return $this->getComplete($request);
        } elseif ($action === 'delete_done') {
			$id = $request->input('id', '');
			$this->deleteDoneById($id);
            return $this->deleteTaskById($id);
        } else {
            return $this->jsonResponse(['status' => 'error', 'message' => 'Invalid action']);
        }
    }
	public function getTaskList()
    {
        $taskName = "task";
        $this->initTask($taskName, "json");

        return response()->json(['status' => 'success', 'task' => $this->task_object[$taskName]]);
    }

	private function addTask(Request $request)
	{
		$this->initTask("task", "json");
		$taskName = "task";
		$namespace = $this->getNameSpace();
		$name = $request->input('name', '');
		$taskContent = $request->input('task_content', '');
		$taskKey = md5($taskContent);
		$id = $request->input('id', $taskKey);
		$task_path = $request->input('task_path', $namespace);
		$task_entity = [
			"namespace" => $namespace,
			"name" => $name,
			"task_path" => $task_path,
			"id" => $id,
			"task_content" => $taskContent,
			"complete_content" => '',
			"done" => false,
			"complete_path" => null,
			"result" => null,
			"submit_time" => Carbon::now(),
			"completion_time" => null,
		];
		$this->task_object[$taskName]["list"][$taskKey] = $task_entity;

		$task_file = $this->task_object[$taskName]["file"];
		#$task_dir = dirname($task_file);
		#Storage::makeDirectory($task_dir);
		Storage::put($task_file, json_encode($this->task_object[$taskName]["list"], JSON_PRETTY_PRINT));
		$task_len  = count($this->task_object[$taskName]["list"]);
		return $this->jsonResponse([
			'status' => 'success',
			'message' => 'Task added successfully and The length is '.$task_len.".",
			'task_length' => count($this->task_object[$taskName]["list"]),
			'submit_time' => Carbon::now(),
			'id' => $id,
			'task_entity' => $task_entity
		]);
	}

	public function deleteTaskById($id)
	{
		$taskName = "task";
		$this->initTask($taskName, "json");
		$taskList = &$this->task_object[$taskName]["list"];

		if (isset($taskList[$id])) {
			$deletedTask = $taskList[$id];
			unset($taskList[$id]);
			$taskFile = $this->task_object[$taskName]["file"];
			#$taskDir = dirname($taskFile);
			#Storage::makeDirectory($taskDir);
			Storage::put($taskFile, json_encode($taskList, JSON_PRETTY_PRINT));
			return response()->json([
				'status' => 'success',
				'message' => 'Task deleted successfully',
				'task_entity' => $deletedTask,
				'current_task_length' => count($taskList)
			]);
		} else {
			return response()->json(['status' => 'error', 'message' => 'Task not found for the provided ID.']);
		}
	}

	public function deleteDoneById($id)
	{
		$taskName = "done";
		$this->initTask($taskName, "json");
		$taskList = &$this->task_object[$taskName]["list"];
		if (isset($taskList[$id])) {
			$deletedTask = $taskList[$id];
			unset($taskList[$id]);
			$taskFile = $this->task_object[$taskName]["file"];
			#$taskDir = dirname($taskFile);
			#Storage::makeDirectory($taskDir);
			Storage::put($taskFile, json_encode($taskList, JSON_PRETTY_PRINT));
			return response()->json([
				'status' => 'success',
				'message' => 'Task deleted successfully',
				'task_entity' => $deletedTask,
				'current_task_length' => count($taskList)
			]);
		} else {
			return response()->json(['status' => 'error', 'message' => 'Task not found for the provided ID.']);
		}
	}

	public function getTaskById($taskId, $taskName = "task")
	{
		$this->initTask($taskName, "json");

		if (isset($this->task_object[$taskName]["list"][$taskId])) {
			$task = $this->task_object[$taskName]["list"][$taskId];

			return response()->json([
				'status' => 'success',
				'success' => true,
				'message' => 'Task found successfully',
				'task_entity' => $task,
			]);
		} else {
			return response()->json(['status' => 'error','success' => false, 'message' => 'Task not found for the provided ID.']);
		}
	}

	public function getComplete(Request $request)
	{
		$taskContent = $request->input('task_content');
		$taskKey = md5($taskContent);
		$id = $request->input('id', $taskKey);
		if ($id === null) {
			return response()->json(['status' => 'error', 'message' => 'task_content and ID are required.']);
		}
		$taskEntity = $this->getCompleteTaskById($id);
		$completeContent = $this->getCompleteContentById($id);
		return response()->json([
			'status' => 'success',
			'task_entity' => $taskEntity,
			'complete_content' => $completeContent,
		]);
	}

	private function getCompleteTaskById($id)
	{
		$completePath = $this->getDoneFile($id . ".json");
		if (!Storage::exists($completePath)) {
			return null;
		}
		$content = Storage::get($completePath);
		$decodedContent = json_decode($content, true);
		return $decodedContent;
	}

    private function getCompleteContentById($id)
    {
        $completePath = $this->getDoneFile($id . ".txt");
        if (!Storage::exists($completePath)) {
            return null;
        }
        return Storage::get($completePath);
    }

	private function updateTaskStatus($id, $done, $resultPath, $completeContent)
	{
		$taskName = "task";
		$this->initTask($taskName, "json");
		$taskList = &$this->task_object[$taskName]["list"];
		if (isset($taskList[$id])) {
			$task = &$taskList[$id];
			$task["done"] = $done;
			$task["completion_time"] = Carbon::now();
			$task["result"] = $resultPath;
			$task["complete_path"] = $this->getDoneFile($id . ".txt");

			if (!empty($completeContent)) {
				Storage::put($task["complete_path"], $completeContent);
			}
			$taskFile = $this->task_object[$taskName]["file"];
			Storage::put($taskFile, json_encode($taskList, JSON_PRETTY_PRINT));
			return true;
		}
		return false;
	}

	public function completeTask(Request $request)
	{
		$taskName = "done";
		$this->initTask($taskName, "json");

		$namespace = $this->getNameSpace($request->input('namespace', 'default'));
		$completeContent = $request->input('complete_content', '');
		$id = $request->input('id', '');
		if (empty($completeContent) || empty($id)) {
			return response()->json(['status' => 'error', 'message' => 'Complete content and ID are required.']);
		}
		$taskEntity = $this->getTaskById($id)->getData();
		if ($taskEntity->success === false) {
			return response()->json(['status' => 'error', 'message' => 'Task not found for the provided ID.']);
		}
		$completePath = $this->getDoneFile($id . ".txt");
		$completeJsonPath = $this->getDoneFile($id . ".json");
		#$taskEntityArray = $taskEntity->getData(true);
		#$taskEntity = $taskEntityArray["task_entity"];
		$updatedTaskEntity = [
			"namespace" => $taskEntity["namespace"],
			"name" => $taskEntity["name"],
			"task_path" => $taskEntity["task_path"],
			"task_content" => $taskEntity["task_content"],
			"complete_content" => $completeContent,
			"done" => true,
			"submit_time" => now(),
			"completion_time" => now(),
			"result" => Storage::url($completeJsonPath),
			"complete_path" => Storage::url($completePath),
		];
		Storage::put($completeJsonPath, json_encode($updatedTaskEntity, JSON_PRETTY_PRINT));
		Storage::put($completePath, $completeContent);
		$this->task_object[$taskName]["list"][$id] = $updatedTaskEntity;
		$taskList = $this->task_object[$taskName]["list"];
		$taskFile = $this->task_object[$taskName]["file"];
		Storage::put($taskFile, json_encode($taskList, JSON_PRETTY_PRINT));
		$this->updateTaskStatus($id, true, $completePath, $completeContent);
		return response()->json(['status' => 'success','task_entity' => $updatedTaskEntity, 'message' => 'Task completed successfully', 'list_length' => count($taskList)]);
	}
}
