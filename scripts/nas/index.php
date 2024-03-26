<?php
function displayDirectory($dir)
{
    $path = isset($_GET['path']) ? $_GET['path'] : '';
    $dirPath = $dir . $path;
    $baseDir = __DIR__;

    if (is_dir($dirPath)) {
        $directory = opendir($dirPath);
        $parentPath = dirname($path);

        // Ensure the parent path doesn't end with a slash to avoid double slashes
        $parentPath = rtrim($parentPath, '/');

        echo "<p><a href='?path=$parentPath'>Back</a></p>";
        echo "<ul>";

        while (($entry = readdir($directory)) !== false) {
            if ($entry != "." && $entry != ".." && $entry != "index.php") {
                $entryPath = $dirPath . '/' . $entry;

                if (is_dir($entryPath)) {
                    echo "<li><a href='?path=$path/$entry'>$entry</a></li>";
                } else {
                    $relativePath = str_replace($baseDir, '', $entryPath);

                    echo "<li>
                            <div class='download-info'>
                                <p><a target='_blank' href='$path/$entry'>$entry</a>
                                <code class='down-element' data-path='$relativePath'></code>
                                    <button class='copy-button' data-path='$relativePath' data-clipboard-text=''>Copy</button>
                                </p>
                            </div>
                          </li>";
                }
            }
        }

        closedir($directory);
        echo "</ul>";
        echo "<p><a href='?path=$parentPath'>Back</a></p>";
        echo "";
    } else {
        echo "<p>Error: Directory '$dirPath' not found.</p>";
    }
}



?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Software Static Library</title>
    <script src='/static_src/js/clipboard.min.js'></script>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f4;
            color: #333;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 800px;
            margin: 50px auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }

        h1 {
            color: #007bff;
        }

        p {
            line-height: 1.6;
        }

        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 11px;
        }

        ul {
            list-style-type: none;
            padding: 0;
        }

        li {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Software Static Library</h1>
        <p>This is a static library for software development.</p>
        <?php
            displayDirectory(__DIR__);
        ?>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.down-element').forEach(function(element) {
                element.textContent = getFullDownloadURL(element.getAttribute('data-path'));
            });

            document.querySelectorAll('.copy-button').forEach(function(button) {
                new ClipboardJS(button);
                button.setAttribute('data-clipboard-text',getFullDownloadURL(button.getAttribute('data-path'))) ;
                button.addEventListener('success', function(e) {
                    alert('URL copied to clipboard: ' + e.text);
                });
            });

            function getFullDownloadURL(relativePath) {
                return window.location.origin + relativePath;
            }
        });
    </script>
</body>
</html>
