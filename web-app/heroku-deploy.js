const ghpages = require('gh-pages');

ghpages.publish(
    '../',
    {
        /*push: false,*/
        add: true,
        branch: 'heroku-app',
        src: [
            'core/**',
            'web-app/build/**',
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
