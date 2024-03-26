class Cluster {
    static getWithParam(paramName) {
        return new Promise((resolve, reject) => {
            $.get(`/${paramName}`, (data) => {
                resolve(data);
            }).fail((error) => {
                reject(error);
            });
        });
    }

    static getWithParamAndData(paramName, data) {
        return new Promise((resolve, reject) => {
            $.get(`/${paramName}`, data, (result) => {
                resolve(result);
            }).fail((error) => {
                reject(error);
            });
        });
    }

    static getClusters() {
        return new Promise((resolve, reject) => {
            $.get('/get_clusters', (clusters) => {
                resolve(clusters);
            }).fail((error) => {
                reject(error);
            });
        });
    }

    static postFormData(selector) {
        const data = {};
        $(`${selector} [data-pm2]`).each(function () {
            const key = $(this).data('pm2');
            const value = $(this).val();
            data[key] = value;
        });

        return new Promise((resolve, reject) => {
            $.post('/post_data', data, (result) => {
                resolve(result);
            }).fail((error) => {
                reject(error);
            });
        });
    }

    static generateHTML(clusters) {
        let htmlCode = '';
        clusters.forEach((cluster) => {
            htmlCode += `<div>Name: ${cluster.name}, Instances: ${cluster.instances}</div>`;
        });
        return htmlCode;
    }
}