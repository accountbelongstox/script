using IWshRuntimeLibrary;
using System;
using System.IO.Compression;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Text;

namespace ddwin.coreTools

{
    public class Tools
    {

        public static void CreateDesktopShortcut(string shortcutName, string targetPath, string iconPath = "")
        {
            var USER_DESKTOP = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);

            WshShell shell = new WshShell();
            IWshShortcut shortcut = (IWshShortcut)shell.CreateShortcut(Path.Combine(USER_DESKTOP, shortcutName + ".lnk"));

            shortcut.TargetPath = targetPath;
            iconPath = GetAbsolutePath(iconPath);

            if (!string.IsNullOrEmpty(iconPath))
            {
                shortcut.IconLocation = iconPath;
            }

            shortcut.Save();
        }

        public static string GetAbsolutePath(string path)
        {
            if (Path.IsPathRooted(path)) // Check if path is already absolute
            {
                return path;
            }
            else
            {
                string rootDirectory = AppDomain.CurrentDomain.BaseDirectory;
                return Path.Combine(rootDirectory, path);
            }
        }

        public static string NormalizePath(string path)
        {
            if (string.IsNullOrEmpty(path))
                return path;

            path = path.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);

            path = path.Replace(Path.AltDirectorySeparatorChar, Path.DirectorySeparatorChar);

            return path;
        }

    }
}