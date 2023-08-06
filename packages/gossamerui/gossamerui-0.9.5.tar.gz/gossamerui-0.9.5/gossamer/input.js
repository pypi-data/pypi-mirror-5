
    // workaround for Firefox's reporting of SELECT values being out of date
    // on a click event
    window.addEventListener(
        'input',
        function(e) {
            var idText, classNameText, classListText, elm = null;
            if (e.target.id) {
                elm = document.querySelector('#' + e.target.id);
                idText = elm.options[elm.selectedIndex].text;
            } else {};
            if (e.target.className) {
                elm = document.querySelector('.' + e.target.className);
                classNameText = elm.options[elm.selectedIndex].text;
            } else {};
            if (e.target.classList.toString()) {
                elm = document.querySelector('.' + e.target.classList.toString());
                classListText = elm.options[elm.selectedIndex].text;
            } else {};
            events.push([
                Date.now(),
                'input', [
                    [e.target.id, idText],
                    [e.target.className, classNameText],
                    [e.target.classList, classListText]
                ]
            ]);
        },
        true
    );
