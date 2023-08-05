'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'myApp.controllers']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/main', {templateUrl: 'templates/main.html', controller: 'MainCtrl1'});
    //$routeProvider.when('/view2', {templateUrl: 'templates/partial2.html', controller: 'MyCtrl2'});
    $routeProvider.otherwise({redirectTo: '/main'});
  }]);
