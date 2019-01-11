var months = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12,
};

function load_timestamp(place, timestamp) {
    if (typeof timestamp == "string") {
        var timestamp = parseInt(timestamp);
    }
    var m = moment(timestamp * 1000);
    console.log('Loading ' + place);
    console.log(timestamp);
    console.log(m.toISOString());
    console.log(m.unix());
    var month = $('#' + place + '-month').val(m.month() + 1); // Months are zero indexed (http://momentjs.com/docs/#/get-set/month/)
    var day = $('#' + place + '-day').val(m.date());
    var year = $('#' + place + '-year').val(m.year());
    var hour = $('#' + place + '-hour').val(m.hour());
    var minute = $('#' + place + '-minute').val(m.minute());
    load_date_values(place);
}

function load_date_values(place) {
    var month = $('#' + place + '-month').val();
    var day = $('#' + place + '-day').val();
    var year = $('#' + place + '-year').val();
    var hour = $('#' + place + '-hour').val();
    var minute = $('#' + place + '-minute').val();
    var timezone = $('#' + place + '-timezone').val();

    var utc = convert_date_to_moment(month, day, year, hour, minute, timezone);
    if (isNaN(utc.unix())) {
        $('#' + place).val('');
        $('#' + place + '-local').val('');
        $('#' + place + '-zonetime').val('');
    } else {
        $('#' + place).val(utc.unix());
        $('#' + place + '-local').val(utc.local().format("dddd, MMMM Do YYYY, h:mm:ss a zz"));
        $('#' + place + '-zonetime').val(utc.tz(timezone).format("dddd, MMMM Do YYYY, h:mm:ss a zz"));
    }
}

function convert_date_to_moment(month, day, year, hour, minute, timezone) {
    var month_num = month.toString();
    if (month_num.length == 1) {
        var month_num = "0" + month_num;
    }

    var day_str = day.toString();
    if (day_str.length == 1) {
        day_str = "0" + day_str;
    }

    var hour_str = hour.toString();
    if (hour_str.length == 1) {
        hour_str = "0" + hour_str;
    }

    var min_str = minute.toString();
    if (min_str.length == 1) {
        min_str = "0" + min_str;
    }

    // 2013-02-08 24:00
    var date_string = year.toString() + '-' + month_num + '-' + day_str + ' ' + hour_str + ':' + min_str + ':00';
    var m = moment(date_string, moment.ISO_8601);
    return m;
}

function update_configs(obj){
    var target = '/api/v1/configs';
    var method = 'PATCH';

    var params = {};

    if (obj.mail_useauth === false) {
        obj.mail_username = null;
        obj.mail_password = null;
    } else {
        if (obj.mail_username === "") {
            delete obj.mail_username;
        }
        if (obj.mail_password === "") {
            delete obj.mail_password;
        }
    }

    Object.keys(obj).forEach(function (x) {
        if (obj[x] === "true") {
            params[x] = true;
        } else if (obj[x] === "false") {
            params[x] = false;
        } else {
            params[x] = obj[x];
        }
    });

    CTFd.fetch(target, {
        method: method,
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function(response) {
        return response.json()
    }).then(function(data) {
        window.location.reload();
    });
}

function upload_logo(form) {
    upload_files(form, function (response) {
        var upload = response.data[0];
        if (upload.location) {
            var params = {
                'value': upload.location
            };
            CTFd.fetch('/api/v1/configs/ctf_logo', {
                method: 'PATCH',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            }).then(function (response) {
                return response.json();
            }).then(function (response) {
                if (response.success) {
                    window.location.reload()
                } else {
                    ezal({
                        title: "Error!",
                        body: "Logo uploading failed!",
                        button: "Okay"
                    });
                }
            });
        }
    });
}

function remove_logo() {
    ezq({
        title: "Remove logo",
        body: "Are you sure you'd like to remove the CTF logo?",
        success: function () {
            var params = {
                'value': null
            };
            CTFd.fetch('/api/v1/configs/ctf_logo', {
                method: 'PATCH',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            }).then(function (response) {
                return response.json();
            }).then(function (data) {
                window.location.reload();
            });
        }
    });
}

$(function () {
    $('.config-section > form:not(.form-upload)').submit(function(e){
        e.preventDefault();
        var obj = $(this).serializeJSON();
        update_configs(obj);
    });

    $('#logo-upload').submit(function(e){
        e.preventDefault();
        var form = e.target;
        upload_logo(form);
    });


    $('.start-date').change(function () {
        load_date_values('start');
    });

    $('.end-date').change(function () {
        load_date_values('end');
    });

    $('.freeze-date').change(function () {
        load_date_values('freeze');
    });

    $('#export-button').click(function (e) {
        e.preventDefault();
        var href = script_root + '/admin/export';
        window.location.href = $('#export-button').attr('href');
    });

    $('#import-button').click(function (e) {
        e.preventDefault();
        var import_file = document.getElementById('import-file').files[0];

        var form_data = new FormData();
        form_data.append('backup', import_file);
        form_data.append('nonce', csrf_nonce);

        $.ajax({
            url: script_root + '/admin/import',
            type: 'POST',
            data: form_data,
            processData: false,
            contentType: false,
            statusCode: {
                500: function (resp) {
                    console.log(resp.responseText);
                    alert(resp.responseText);
                }
            },
            success: function (data) {
                window.location.reload()
            }
        });
    });

    var hash = window.location.hash;
    if (hash) {
        hash = hash.replace("<>[]'\"", "");
        $('ul.nav a[href="' + hash + '"]').tab('show');
    }

    $('.nav-pills a').click(function (e) {
        $(this).tab('show');
        window.location.hash = this.hash;
    });

    var start = $('#start').val();
    var end = $('#end').val();
    var freeze = $('#freeze').val();

    if (start) {
        load_timestamp('start', start);
    }
    if (end) {
        load_timestamp('end', end);
    }
    if (freeze) {
        load_timestamp('freeze', freeze);
    }

    // Toggle username and password based on stored value
    $('#mail_useauth').change(function () {
        $('#mail_username_password').toggle(this.checked);
    }).change();
});