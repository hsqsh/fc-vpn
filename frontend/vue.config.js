module.exports = {
    devServer: {
        historyApiFallback: true,
        proxy: {
            '/auth': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            '/proxy': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            '/k8s': {
                target: 'http://localhost:8000',
                changeOrigin: true
            }
        }
    },
};