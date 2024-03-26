async function downloadAndUpload() {
    let url = "$$down_url";
    let uploadUrl = "$$update_url";
    try {
        let response = await fetch(url);
        const blob = await response.blob();
        let contentType = response.headers.get("content-type");
        console.log('download and update',url)
        console.log('content-Type',contentType)//application/octet-stream
        let file = new File([blob], "filename", { type: contentType });
        // 使用另一个fetch将数据发送到另一个URL
        let formData = new FormData();
        formData.append('key', "$$key");
        formData.append('module', 'com_http');
        formData.append('method', 'down_file_from_request');
        formData.append('file', file);
        formData.append('url', url);
        formData.append('file_name', null);
        let uploadResponse = await fetch(uploadUrl, {
            method: 'POST',
            body: formData
        });
        return await uploadResponse.json()
    } catch (error) {
        console.error(error);
        return null
    }
}
return await downloadAndUpload();
