using Masuit.Tools;
using System;
using IWshRuntimeLibrary;
using System.IO;
using SystemFile = System.IO.File;
using Masuit.Tools.Models;
using System.IO.Compression;
using System.Net;
using ddwin.coreTools;

namespace ddwin.installerClass
{
    public class AutoInstaller
    {
        private string SCRIPT_NAME;
        private string FILE_PATH;
        private string USER_DESKTOP;
        private string MAIN_URL;
        private string INSTALLER_URL_PATH;
        private string INSTALLER_PROCESS_FILE;
        private string INSTALLER_INIT_FILE;
        private string BASE_INSTALL_FILE;


        public void Start()
        {

            //#           1.检测.desktop_by_node用户文件夹是否存在
            //            2.获取当前系统可用空间最大盘符
            //            2.根据盘符得到applicattions的地址 ，例如D: applicattions,同时获得 lang_compiler的地址
            //            4,开始向服务器得到python3.9/3.10的远程下载地址，然后下载并解压到 lang_compiler目录  （但如果已经存在则不用下载）
            //            5，添加一个类到 coreTools/EnvRead.cs 用于读取当前程序根目录的.env文件 （直接从init_start.py的 class Env :  ）
            //            6，添加一个类到 coreTools/Settings.cs 用于读取当前程序根目录的.json文件 （直接从init_start.py的 class Settings :  ）
            //            7, 添加一个类到 coreTools/Winget.cs （直接从init_start.py的 class Winget :  ）
            //            8, 添加一个到 coreTools/Tools.cs （直接从init_start.py的def read_file, def save_file, :  ）

            //                程序组织
            //                以上程序的动作方法，统一放到coreTools/Tools中，比如下载方法，
            //                以上程序的全局变量提供，统一放到 Resource中提供，比如远程服务器地址  
            //                工具类可以调用 Resource 获取必要的信息，但Resource不能调用其他类，以防循环
            //                AutoInstaller（逻辑类）可以调用 coreTools / Tools 工具类和 Resource编写小逻辑。


            var maxDriver = Resource.GetMaxDriver();
            MessageBox.Show(maxDriver, "maxDriver", MessageBoxButtons.OK, MessageBoxIcon.Information);


            MessageBox.Show("Hello, world!", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
            SetupDesktopEnvironment();


        }

        public static void Click(object sender, EventArgs e)
        {
            var isEmail = "abcd@qq.com".MatchEmail();
            MessageBox.Show("isEmail:" + isEmail.isMatch, "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);

        }

        public void SetupDesktopEnvironment()
        {
            string desktopDir = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
            Environment.SetEnvironmentVariable("DESKTOP_DIR", desktopDir);
            string appDataDir = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            Environment.SetEnvironmentVariable("USER_APPDATA", appDataDir);
            string userDesktopDir = Path.Combine(appDataDir, ".desktop_by_node");
            if (!Directory.Exists(userDesktopDir))
            {
                Directory.CreateDirectory(userDesktopDir);
            }
            Environment.SetEnvironmentVariable("USER_DESKTOP", userDesktopDir);
            MessageBox.Show(userDesktopDir, "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        public void UpdateScripts()
        {
        }

        private void UpdateScript(string localScriptPath, string remoteScriptName)
        {
        }


        private void AddToStartupFolder()
        {
        }

        private void AutoUpdate()
        {
        }

        private void SetWshShell()
        {
        }

        private void SetShellLink(string targetPath, string description, string iconLocation)
        {
        }
    }
}