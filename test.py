import subprocess

# 假设 'example.bat' 是你想要运行的批处理文件的路径
bat_file_path = 'example.bat'

# 使用 subprocess.run() 执行 .bat 文件
result = subprocess.run([bat_file_path], capture_output=True, text=True)

# 打印输出结果
print("标准输出:", result.stdout)

# 如果需要处理错误输出
print("标准错误:", result.stderr)

# 检查程序是否成功执行
if result.returncode == 0:
    print("批处理文件执行成功")
else:
    print("批处理文件执行失败")