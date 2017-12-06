$(function() {

    Morris.Area({
        element: 'morris-area-chart',
        data: [{
            period: '2011',
            neutrogena: 381,
            coppertone: 150,
            bananaboat: 154
        }, {
            period: '2012',
            neutrogena: 311,
            coppertone: 258,
            bananaboat: 190
        }, {
            period: '2013',
            neutrogena: 405,
            coppertone: 213,
            bananaboat: 98
        }, {
            period: '2014',
            neutrogena: 287,
            coppertone: 122,
            bananaboat: 124
        }, {
            period: '2015',
            neutrogena: 54,
            coppertone: 50,
            bananaboat: 38
        }, {
            period: '2016',
            neutrogena: 166,
            coppertone: 27,
            bananaboat: 33
        }, {
            period: '2017',
            neutrogena: 108,
            coppertone: 17,
            bananaboat: 28
        }],
        xkey: 'period',
        ykeys: ['neutrogena', 'coppertone', 'bananaboat'],
        labels: ['Neutrogena', 'Coppertone', 'Banana Boat'],
        pointSize: 2,
        hideHover: 'auto',
        resize: true
    });

   

    Morris.Bar({
        element: 'morris-bar-chart',
        data: [{
            y: 'January',
            a: 80
        }, {
            y: 'Febraury',
            a: 49
        }, {
            y: 'March',
            a: 52
        }, {
            y: 'April',
            a: 66
        }, {
            y: 'May',
            a: 85
        }, {
            y: 'June',
            a: 110
        }, {
            y: 'July',
            a: 118
        },{
            y: 'August',
            a: 52
        }, {
            y: 'September',
            a: 66
        }, {
            y: 'October',
            a: 55
        }, {
            y: 'November',
            a: 49
        }, {
            y: 'December',
            a: 53
        }],
        xkey: 'y',
        ykeys: ['a'],
        labels: ['Series A'],
        hideHover: 'auto',
        resize: true
    });
    
});
