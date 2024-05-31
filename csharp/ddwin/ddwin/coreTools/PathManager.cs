using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace ddwin.coreTools
{
    public class PathManager
    {
        private string[] SupportedCommands = { "add", "remove", "is", "show" };

        public PathManager()
        {
        }

        public string[] GetCurrentPath()
        {
            string result = GetCurrentQuery();
            string regType = GetPathType(result);
            string pathsMatch = result.Split(regType)[1].Trim();
            string[] cleanedPaths = pathsMatch.Split(';');
            List<string> formattedPaths = new List<string>();
            foreach (string p in cleanedPaths)
            {
                if (!string.IsNullOrWhiteSpace(p))
                {
                    formattedPaths.Add(Tools.NormalizePath(p.Trim()));
                }
            }
            return formattedPaths.ToArray();
        }

        public string GetPathType(string result = "", string defaultRegType = "REG_SZ")
        {
            if (string.IsNullOrEmpty(result))
            {
                result = GetCurrentQuery();
            }
            string[] parts = result.Split();
            foreach (string part in parts)
            {
                if (part.StartsWith("REG_"))
                {
                    return part;
                }
            }
            return defaultRegType;
        }

        private string GetCurrentQuery()
        {
            ProcessStartInfo processInfo = new ProcessStartInfo
            {
                FileName = "reg.exe",
                Arguments = "query \"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment\" /v Path",
                RedirectStandardOutput = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            Process process = new Process { StartInfo = processInfo };
            process.Start();
            string result = process.StandardOutput.ReadToEnd();
            process.WaitForExit();
            process.Close();
            return result;
        }
        public static void BackupEnvPath(string[] currentPath)
        {
            // Get the directory where backup files are stored
            string backupDir = Path.GetTempPath();

            // Get all old backup files matching the specified pattern and order them by creation time
            string[] oldBackupFiles = Directory.GetFiles(backupDir, "$SetPath_bak_*.bak")
                                               .OrderBy(f => new FileInfo(f).CreationTime)
                                               .ToArray();

            // Calculate the number of files to delete to maintain a maximum of 30 backups
            int filesToDelete = oldBackupFiles.Length - 30;

            // Delete excess backup files
            for (int i = 0; i < filesToDelete; i++)
            {
                File.Delete(oldBackupFiles[i]);
            }

            // Create a new backup file with current path information
            string backupTmpFile = Path.Combine(backupDir, $"$SetPath_bak_{DateTime.Now.ToString("yyyyMMdd_HHmmss")}.bak");
            string currentPathString = string.Join(";", currentPath);
            File.WriteAllText(backupTmpFile, currentPathString);

            // Output the path of the backup file
            Console.WriteLine($"Backup file saved to: {backupTmpFile}");

            // Output the number of old backup files cleaned up
            if (filesToDelete > 0)
            {
                Console.WriteLine($"Cleaned up {filesToDelete} outdated or redundant files.");
            }
        }


        public void AddPath(string newPath)
        {
            newPath = Path.GetFullPath(newPath);
            string[] currentPath = GetCurrentPath();
            if (!currentPath.Contains(newPath))
            {
                List<string> updatedPath = currentPath.ToList();
                updatedPath.Add(newPath);
                BackupEnvPath(updatedPath.ToArray());
                UpdatePathRegistry(updatedPath);
            }
            else
            {
                Console.WriteLine($"The path '{newPath}' already exists in the environment.");
            }
        }

        private void UpdatePathRegistry(List<string> updatedPath)
        {
            string regType = GetPathType("", "REG_SZ");
            string addPath = string.Join(";", updatedPath);
            ProcessStartInfo processInfo = new ProcessStartInfo
            {
                FileName = "reg.exe",
                Arguments = $"add \"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment\" /v Path /t {regType} /d \"{addPath}\" /f",
                RedirectStandardOutput = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            Process process = new Process { StartInfo = processInfo };
            process.Start();
            string result = process.StandardOutput.ReadToEnd();
            process.WaitForExit();
            process.Close();
            Console.WriteLine(result);
        }

        public void RemovePath(string pathToRemove)
        {
            pathToRemove = Path.GetFullPath(pathToRemove);
            string[] currentPath = GetCurrentPath();
            if (currentPath.Contains(pathToRemove))
            {
                List<string> updatedPath = currentPath.ToList();
                updatedPath.Remove(pathToRemove);
                BackupEnvPath(updatedPath.ToArray());
                UpdatePathRegistry(updatedPath);
            }
            else
            {
                Console.WriteLine($"currentPath:");
                foreach (var path in currentPath)
                {
                    Console.WriteLine("\t" + path);
                }
                Console.WriteLine($"The path '{pathToRemove}' does not exist in the environment.");
            }
        }

        public bool IsPath(string pathToCheck)
        {
            pathToCheck = Path.GetFullPath(pathToCheck);
            string[] currentPath = GetCurrentPath();
            return currentPath.Contains(pathToCheck);
        }

    }
}
