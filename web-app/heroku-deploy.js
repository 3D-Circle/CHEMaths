const ghpages = require('gh-pages');

ghpages.publish(
    '../../CHEMaths_Release',
    {
        branch: 'heroku-app',
        src: [
            'core/**',
            'web-app/build/**',
            'Procfile',
            'requirements.txt',
            'runtime.txt',
            'app.py',
        ]
    },
    function(err) {
        if (err) {
            console.log(err);
        } else {
            console.log("Push success !");
        }
    }
);
