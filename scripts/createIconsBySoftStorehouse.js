const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class IconExtractor {
    constructor(directories) {
        this.directories = directories;
    }

    async getIconAsBase64(filePath) {
        try {
            const iconPath = `${filePath}.ico`;
            const cmd = `powershell -command "Add-Type -AssemblyName System.Drawing; [System.Drawing.Icon]::ExtractAssociatedIcon('${filePath}').ToBitmap().Save('${iconPath}', [System.Drawing.Imaging.ImageFormat]::Icon);"`;
			execSync(cmd);
            const iconData = fs.readFileSync(iconPath);
            fs.unlinkSync(iconPath);
            return `data:image/x-icon;base64,${iconData.toString('base64')}`;
        } catch (error) {
            console.error(`Error getting icon for ${filePath}:`, error);
            return 'YOUR_BASE64_PLACEHOLDER_IMAGE';
        }
    }

    getFilesRecursive(folderPath) {
        let fileList = [];
        const files = fs.readdirSync(folderPath);

        for (const file of files) {
            const fullPath = path.resolve(folderPath, file);  // Get the absolute path here
            const stat = fs.statSync(fullPath);

            if (stat.isDirectory()) {
                fileList = fileList.concat(this.getFilesRecursive(fullPath));
            } else {
                fileList.push(fullPath);
            }
        }

        return fileList;
    }

    generateTree(files) {
        const tree = {};

        for (const file of files) {
            const parts = file.split(path.sep);
            let currentLevel = tree;

            for (let i = 0; i < parts.length; i++) {
                const part = parts[i];

                if (!currentLevel[part]) {
                    if (i === parts.length - 1) {
                        currentLevel[part] = { __path: file };
                    } else {
                        currentLevel[part] = {};
                    }
                }
                currentLevel = currentLevel[part];
            }
        }

        return tree;
    }

    async generateHTML(tree, level = 0) {
        let html = '';

        for (const [key, value] of Object.entries(tree)) {
            if (key === '__path') {
                html += `<img src="${await this.getIconAsBase64(value)}" alt="${key}">${key}<br>`;
            } else {
                html += `${'&nbsp;'.repeat(level * 4)}${key}<br>`;
                html += await this.generateHTML(value, level + 1);
            }
        }

        return html;
    }

    async execute() {
        let files = [];

        for (const dir of this.directories) {
            const absoluteDir = path.resolve(dir);
            files = files.concat(this.getFilesRecursive(absoluteDir));
        }

        const tree = this.generateTree(files);
        const htmlContent = await this.generateHTML(tree);

        fs.writeFileSync('output.html', htmlContent);
    }
}

const directories = ['softs', 'applications'];
const extractor = new IconExtractor(directories);
extractor.execute();
