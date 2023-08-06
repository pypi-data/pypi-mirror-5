// TODO(cramer): this should be defined elsewhere
var Sentry = angular.module('Sentry', []);

Sentry.factory('GroupModel', function() {
    var GroupModel = function GroupModel(data) {
        angular.copy(data, this);
    };
    var proto = GroupModel.prototype;

    proto.getLevelClassName = function() {
        return 'level-' + this.levelName;
    };

    // updateResolved: function(){
    //     if (this.model.get('isResolved')) {
    //         this.$el.addClass('resolved');
    //     } else {
    //         this.$el.removeClass('resolved');
    //     }
    // },

    // renderSparkline: function(obj){
    //     var data = this.model.get('historicalData');
    //     if (!data || !data.length)
    //         return;

    //     this.$el.addClass('with-sparkline');

    //     app.charts.createSparkline(this.$el.find('.sparkline'), data);
    // },

    // resolve: function(){
    //     $.ajax({
    //         url: this.getResolveUrl(),
    //         type: 'post',
    //         dataType: 'json',
    //         success: _.bind(function(response) {
    //             this.model.set('version', response.version);
    //             this.model.set('isResolved', true);
    //         }, this)
    //     });
    // },

    // unresolve: function(){
    //     $.ajax({
    //         url: this.getUnresolveUrl(),
    //         type: 'post',
    //         dataType: 'json',
    //         success: _.bind(function(response) {
    //             this.model.set('version', response.version);
    //             this.model.set('isResolved', false);
    //         }, this)
    //     });
    // },

    // getResolveUrl: function(){
    //     return app.config.urlPrefix + '/api/' + app.config.teamId + '/' +
    //             app.config.projectId + '/group/' + this.model.get('id') +
    //             '/set/resolved/';
    // },

    // getUnresolveUrl: function(){
    //     return app.config.urlPrefix + '/api/' + app.config.teamId + '/' +
    //             app.config.projectId + '/group/' + this.model.get('id') +
    //             '/set/unresolved/';
    // },

    // getBookmarkUrl: function(){
    //     return app.config.urlPrefix + '/api/' + app.config.teamId + '/' + app.config.projectId + '/bookmark/';
    // },

    // bookmark: function(){
    //     $.ajax({
    //         url: this.getBookmarkUrl(),
    //         type: 'post',
    //         dataType: 'json',
    //         data: {
    //             gid: this.model.get('id')
    //         },
    //         success: _.bind(function(response){
    //             this.model.set('version', response.version);
    //             this.model.set('isBookmarked', response.isBookmarked);
    //         }, this)
    //     });
    // },

    // updateLastSeen: function(){
    //     this.$el.find('.last-seen')
    //         .text(app.utils.prettyDate(this.model.get('lastSeen')))
    //         .attr('title', this.model.get('lastSeen'));
    // },

    // updateCount: function(){
    //     var new_count = app.utils.formatNumber(this.model.get('count'));
    //     var counter = this.$el.find('.count');
    //     var digit = counter.find('span');

    //     if (digit.is(':animated'))
    //         return false;

    //     if (counter.data('count') == new_count) {
    //         // We are already showing this number
    //         return false;
    //     }

    //     counter.data('count', new_count);

    //     var replacement = $('<span></span>', {
    //         css: {
    //             top: '-2.1em',
    //             opacity: 0
    //         },
    //         text: new_count
    //     });

    //     // The .static class is added when the animation
    //     // completes. This makes it run smoother.

    //     digit.before(replacement).animate({
    //         top: '2.5em',
    //         opacity: 0
    //     }, 'fast', function(){
    //         digit.remove();
    //     });

    //     replacement.delay(100).animate({
    //         top: 0,
    //         opacity: 1
    //     }, 'fast');
    // }

    return GroupModel;
});

Sentry.controller('StreamCtrl', ['$scope', 'initial', 'GroupModel', function($scope, initial, GroupModel){
    $scope.groups = initial.groups.map(function(val) {
        return new GroupModel(val);
    });

    // TODO(cramer): figure out how to better define utilities in Angular apps.\
    $scope.utils = app.utils;
}]);
