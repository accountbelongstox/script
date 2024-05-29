using System;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using System.Net;
using System.Threading.Tasks;
using System.Linq;
using System.Collections.Generic;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;
using System.Text.RegularExpressions;

namespace ddwin.coreTools
{
    public class Resource
    {

        public static string GetMainPath(string relativePath = "", bool createIfNotExists = true)
        {
            string path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".desktop_by_node", relativePath);
            if (createIfNotExists && !Directory.Exists(path))
            {
                Directory.CreateDirectory(path);
            }
            return path;
        }

        public static string GetMainInfoPath(string relativePath = "", bool createIfNotExists = true)
        {
            string path = GetMainPath(".info", createIfNotExists: createIfNotExists);
            if (!string.IsNullOrEmpty(relativePath))
            {
                path = Path.Combine(path, relativePath);
            }
            return path;
        }

        public static string GetAppDir(string relativePath = "", bool createIfNotExists = true)
        {
            string path = Path.Combine(GetMaxDriver(), "applications");
            if (createIfNotExists && !Directory.Exists(path))
            {
                Directory.CreateDirectory(path);
            }
            if (!string.IsNullOrEmpty(relativePath))
            {
                path = Path.Combine(path, relativePath);
            }
            return path;
        }

        public static string GetLangDir(string relativePath = "", bool createIfNotExists = true)
        {
            string path = Path.Combine(GetMaxDriver(), "lang_compiler");
            if (createIfNotExists && !Directory.Exists(path))
            {
                Directory.CreateDirectory(path);
            }
            if (!string.IsNullOrEmpty(relativePath))
            {
                path = Path.Combine(path, relativePath);
            }
            return path;
        }

        public static string GetProgramDir(string relativePath = "", bool createIfNotExists = true)
        {
            string path = Path.Combine(GetMaxDriver(), "programing");
            if (createIfNotExists && !Directory.Exists(path))
            {
                //x
                Directory.CreateDirectory(path);
            }
            if (!string.IsNullOrEmpty(relativePath))
            {
                path = Path.Combine(path, relativePath);
            }
            return path;
        }

        public static string GetDesktopDir(string relativePath = "")
        {
            string programDir = GetProgramDir("desktop_by_node", createIfNotExists: false);
            string path = Path.Combine(programDir, relativePath);
            return path;
        }

        public static string GetEnvironmentsDir(string relativePath = "", bool createIfNotExists = true)
        {
            string path = Path.Combine(GetLangDir("environments"));
            if (createIfNotExists && !Directory.Exists(path))
            {
                Directory.CreateDirectory(path);
            }
            if (!string.IsNullOrEmpty(relativePath))
            {
                path = Path.Combine(path, relativePath);
            }
            return path;
        }

        public static string GetMaxDriver()
        {
            DriveInfo[] drives = DriveInfo.GetDrives();
            var driveSpaces = drives.ToDictionary(d => d.Name, d => d.AvailableFreeSpace);
            string baseDrive = "C:\\";
            long maxSpace = 0;
            foreach (var kvp in driveSpaces)
            {
                if (kvp.Value > maxSpace)
                {
                    maxSpace = kvp.Value;
                    baseDrive = kvp.Key;
                }
            }
            return baseDrive;
        }


        public static List<string> DirectoryPath()
        {
            string[] drives = Directory.GetLogicalDrives();
            List<string> directories = new List<string>();
            string[] searchFolders = { "applications", "lang_compiler" };

            foreach (string drive in drives)
            {
                foreach (string folder in searchFolders)
                {
                    try
                    {
                        string[] foundDirectories = Directory.GetDirectories(drive, folder, SearchOption.AllDirectories);
                        foreach (string dir in foundDirectories)
                        {
                            Console.WriteLine(dir);
                            directories.Add(dir);
                        }
                    }
                    catch (UnauthorizedAccessException)
                    {
                        // Ignore this exception and continue with the next directory.
                    }
                }
            }

            return directories;
        }

        Resource resourcev = new Resource();

    }




}










