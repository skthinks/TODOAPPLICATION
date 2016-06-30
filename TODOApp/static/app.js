(function(){
    var app = angular.module('todo', ['ngCookies']);

    app.controller('LoginController', function($scope, $cookies){
        this.getCred = function(product){
            var http = new XMLHttpRequest()
            var url = "/users/sessions/"
            http.onreadystatechange = function() {
                if (http.readyState == 4 && http.status == 200) {
                    var myArr = JSON.parse(http.responseText);
                    $cookies.put('TOKEN', myArr.token);
                    $cookies.put('user_id', myArr.user_id);
                    window.location = "/static/schedule.html";
                }
            };
            http.open("POST", url, true);
            http.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            http.send(JSON.stringify({email: $scope.loginCtrl.email, password: $scope.loginCtrl.password}));
        }
    });

        
    app.controller('RegisterController', function($scope, $cookies){
        this.getCred = function(product){
            var http = new XMLHttpRequest()
            var url = "/users/"
            http.onreadystatechange = function() {
                if (http.readyState == 4 && http.status == 201) {
                    var myArr = JSON.parse(http.responseText);
                    window.location = "/static/index.html";
                }
            };
            http.open("POST", url, true);
            http.setRequestHeader("Content-Type", "application/json");
            http.send(JSON.stringify({first_name: $scope.regCtrl.firstName, last_name: $scope.regCtrl.lastName, email: $scope.regCtrl.email, password: $scope.regCtrl.password, 
            verified: true}));
        }
    });


    app.controller('ScheduleController', function($scope, $cookies, $http){
        var schedCtrl = this;
        schedCtrl.tasks = []
        schedCtrl.tasksToday = []
        this.getSched = function(){
            var u_id = $cookies.get('user_id');
            var token = $cookies.get('TOKEN');
            url = "/schedule/id/" + u_id;
            $http({
                method: 'GET',
                url: url,
                headers: {
                    'TOKEN': token,
                    'safasf': "asflnalf"
                }
            }).then(function successCallback(response) {
                schedCtrl.tasks = response.data.data;
                for(i=0; i< (schedCtrl.tasks).length; i++){
                    task_datetime = response.data.data[i].scheduled_time;
                    task_date = task_datetime.substr(0,10);
                    var date = new Date();
                    var mm = date.getMonth()+1; 
                    var dd = date.getDate();
                    var yyyy = date.getFullYear();
                    if(dd<10) {
                        dd='0'+dd
                    } 

                    if(mm<10) {
                        mm='0'+mm
                    } 

                    date = yyyy+'-'+mm+'-'+dd;
                    if (date == task_date){
                        schedCtrl.tasksToday.push(response.data.data[i]);
                    }

                }
            },function errorCallback(response){
            });
        }
        this.getSched();
    });

     
    app.controller('ScheduleEditController', function($scope, $cookies, $http){
        this.getSched = function(task){
            $cookies.put('TASK_ID', task.id) 
            window.location = "/static/editschedule.html";
        }
    });

    
    app.controller('EditController', function($scope, $cookies, $http){
        this.edit = function(){
            var u_id = $cookies.get('user_id');
            var token = $cookies.get('TOKEN');
            var task_id = $cookies.get('TASK_ID');
            var task = $scope.editCtrl.task;
            var time = $scope.editCtrl.schedTime;
            var url = "/schedule/id/" + u_id + "/";
            $http({
                method: 'PUT',
                url: url,
                headers: {
                    'TOKEN': token,
                    'safasf': "asflnalf"
                },
                data: {
                    'parameter_id': task_id,
                    'user_id': u_id,
                    'task': task,
                    'scheduled_time': time,
                    'checked': true    
                }
            }).then(function successCallback(response) {
                $cookies.remove('TASK_ID')
                window.location = "/static/schedule.html"
            },function errorCallback(response){
            });
        }
    });

    
    app.controller('PostController', function($scope, $cookies, $http){
        this.post = function(){
            var u_id = $cookies.get('user_id');
            var token = $cookies.get('TOKEN');
            var task = $scope.postCtrl.task;
            var time = $scope.postCtrl.schedTime;
            var url = "/schedule/";
            $http({
                method: 'POST',
                url: url,
                headers: {
                    'TOKEN': token,
                    'safasf': "asflnalf"
                },
                data: {
                    'user_id': u_id,
                    'task': task,
                    'scheduled_time': time,
                    'checked': true    
                }
            }).then(function successCallback(response) {
                window.location = "/static/schedule.html"
            },function errorCallback(response){
            });
        }
    });




    app.controller('ScheduleDeleteController', function($scope, $cookies, $http){
        this.delSched = function(task){
            var u_id = $cookies.get('user_id');
            var token = $cookies.get('TOKEN');
            var task_id = task.id;
            var time = task.scheduled_time;
            var url = "/schedule/id/" + u_id +  "/";
            $http({
                method: 'PUT',
                url: url,
                headers: {
                    'TOKEN': token,
                    'safasf': "asflnalf"
                },
                data: {
                    'parameter_id': task_id,
                    'user_id': u_id,
                    'task': task,
                    'scheduled_time': time,
                    'checked': false  
                }
            }).then(function successCallback(response) {
                window.location = "/static/schedule.html"
            },function errorCallback(response){
            });
        }
    });



    app.controller('LogoutController', function($scope, $cookies, $http){
        this.logout = function(){
            var u_id = $cookies.get('user_id');
            var token = $cookies.get('TOKEN');
            var url = "/users/sessions/" + token +  "/";
            $http({
                method: 'GET',
                url: url
            }).then(function successCallback(response) {
                $cookies.remove('TOKEN');
                $cookies.remove('user_id');
                window.location = "/static/index.html"
            },function errorCallback(response){
            });
        }
    });



    app.controller('TabController', ['$scope', function($scope) {
        $scope.tab = 1;
        $scope.setTab = function(newTab){
            $scope.tab = newTab;
        };
        $scope.isSet = function(tabNum){
            return $scope.tab === tabNum;
        };
    }]);

})();
