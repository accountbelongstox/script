/*!
 * mqScroll 1.0.0
 * Author: SuperFace
 * GitHub: https://github.com/SuperFace/SVGPie
 * Date: 2019-11-17
 */
var SVGPie = (function(){
	var defaults = {
        easing: 'easeOutCubic',
        dimension: 200,
        percentage: 50,
        duration: 2000,
        drawType: "fill",//fill or stroke
        draw: {"circle1": {"fillColor": "#1ABC9C"}, "circle2": {"strokeColor": "#3498DB"}},
        onStart: function() {},
        onComplete: function() {}
    };
	$.extend($.easing, {
        easeOutCubic: function(x, t, b, c, d) {
            return c * ((t = t / d - 1) * t * t + 1) + b;
        }
    });
	// 检测是否为 DOM 元素
    var isElement = function(o){
      if(o && (typeof HTMLElement === 'function' || typeof HTMLElement === 'object') && o instanceof HTMLElement) {
        return true;
      } else {
        return (o && o.nodeType && o.nodeType === 1) ? true : false;
      };
    };

    // 检测是否为 jQuery 对象
    var isJquery = function(o){
      return (o && o.length && (typeof jQuery === 'function' || typeof jQuery === 'object') && o instanceof jQuery) ? true : false;
    };
	var SVGPie = function(obj, perEle,options){
		this.element = obj;
		this.percentageNumEle = perEle;
        this.settings = $.extend({}, defaults, options);
        this._defaults = defaults;
        this.init();
	};
	$.extend(SVGPie.prototype, {

        init: function() {
        	if(!this.element) return;
            this.element.css({
                'width': this.settings.dimension + 'px',
                'height': this.settings.dimension + 'px'
            });
            this.createSvg();
            this.animateNumber();
            this.animateStrokeDasharray();
        },

        createSvg: function() {
            var half = this.settings.dimension / 2;
            var quarter = this.settings.dimension / 4;
            var area = Math.PI * 2 * quarter;
            var circle1Style = this.settings.drawType == "fill" 
            		? "fill:" + this.settings.draw.circle1.fillColor + ";" 
            		: "fill:rgba(0,0,0,0);stroke: " + this.settings.draw.circle1.strokeColor + ";stroke-width: " + this.settings.draw.circle1.strokeWidth + ";"
    		var circle2Style = this.settings.drawType == "fill" 
        		? "fill:" + this.settings.draw.circle1.fillColor + ";stroke: " + this.settings.draw.circle2.strokeColor + ";" 
        		: "fill:rgba(0,0,0,0);stroke: " + this.settings.draw.circle2.strokeColor + ";"
            var svg =
                '<svg xmlns:svg="http://www.w3.org/2000/svg"' +
                'xmlns="http://www.w3.org/2000/svg"' +
                ' style="width:100%;height:100%;-webkit-transform: rotate(-90deg);transform: rotate(-90deg);overflow:visible;">' +

                '<circle r="' + half +
                '" cx="' + half +
                '" cy="' + half +
                '" style="' + circle1Style + '" />' +

                '<circle r="' + (quarter + 0.5) + // +0.5 to debug non-webkit based browsers
                '" cx="' + half +
                '" cy="' + half + '"' +
                'style="' + circle2Style + 'stroke-width:' + half + 'px;' +
                'stroke-dasharray:' + '0px' + ' ' + area + ';' +
                '"/>' +

                '</svg>';

            this.element.prepend(svg);
        },

        animateNumber: function() {
        	if(!this.percentageNumEle) return;
            var $target = this.percentageNumEle;

            $({
                percentageValue: 0
            }).animate({
                percentageValue: this.settings.percentage
            }, {

                duration: this.settings.duration,

                easing: this.settings.easing,

                start: this.settings.onStart,

                step: function() {
                    // Update the element's text with rounded-up value:
                    $target.text(Math.round(this.percentageValue) + '%');
                },

                complete: this.settings.onComplete
            });
        },

        animateStrokeDasharray: function() {
            var debug = this.settings.percentage >= 100 ? 1 : 0; // to debug non webkit browsers
            var area = 2 * Math.PI * ((this.settings.dimension / 4) + 0.4); // +0.4 to debug non webkit browsers
            var strokeEndValue = (this.settings.percentage + debug) * area / 100;
            var $target = this.element.find('svg circle:nth-child(2)');

            $({
                strokeValue: 0
            }).animate({
                strokeValue: strokeEndValue
            }, {

                duration: this.settings.duration,

                easing: this.settings.easing,

                step: function() {
                    $target.css('stroke-dasharray', this.strokeValue + 'px' + ' ' + area + 'px');
                }
            });

        }

    });
	return function(o, p, s){
		var obj = null, perEle = null, settings = {};
		if (o) {
            if(isJquery(o)) obj = o;
            if (isElement(o)) {
                obj = $(o);
            }
        }
		if(p){
			if(isJquery(p)) perEle = p;
            if (isElement(p)) {
            	perEle = $(p);
            }
		}
		if(s){
			if (typeof s === 'object') {
	            settings = s;
	        }
		}
        var svgPie = new SVGPie(obj, perEle, settings);
        return svgPie.settings;
	};
})();