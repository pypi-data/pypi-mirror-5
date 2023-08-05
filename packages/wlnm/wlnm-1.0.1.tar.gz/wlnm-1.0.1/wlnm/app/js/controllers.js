'use strict';

/* Controllers */

angular.module('myApp.controllers', []).
  controller('MainCtrl1', ['$scope', '$http',function ($scope, $http) {
	$scope.prompt = "Machine:" + $scope.prompt
	$scope.update = function(command) {
		if (command) {
			$http.get('/command/'+command).success(function(data) {
			    data = data.replace("[1m","");
				data = data.replace("[0m","");
				$scope.output = data
			});
			if (command.substring(0, 3)=="use")
			{
				$scope.prompt = "Machine:" + command.substring(4)
			}
		}
	    $scope.command='';
	};
	
	
  }])
  /*
  .controller('MyCtrl2', ['$scope',function($scope) {
		var sock = new SockJS('http://192.168.80.140:9999/command');
	    
        $scope.messages = [];
        $scope.sendMessage = function() {
        	if ($scope.messageText) {
            	sock.send($scope.messageText);
        	}
            $scope.messageText = "";
        };

        sock.onmessage = function(e) {
            $scope.messages.push(e.data);
            $scope.$apply();
        };
    
  }]);
  */
