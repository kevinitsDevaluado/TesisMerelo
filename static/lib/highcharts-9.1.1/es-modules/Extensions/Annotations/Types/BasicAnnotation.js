       labelOrShape.point &&
                    labelOrShape.point.yAxis] || axes[1]
            ];
        }, []);
        this.clipXAxis = linkedAxes[0];
        this.clipYAxis = linkedAxes[1];
    };
    Annotation.prototype.getClipBox = function () {
        if (this.clipXAxis && this.clipYAxis) {
            return {
                x: this.clipXAxis.left,
                y: this.clipYAxis.top,
                width: this.clipXAxis.width,
                height: this.clipYAxis.height
            };
        }
    };
    Annotation.prototype.setLabelCollector = function () {
        var annotation = this;
        annotation.labelCollector = function () {
            return annotation.labels.reduce(function (labels, label) {
                if (!label.options.allowOverlap) {
                    labels.push(label.graphic);
                }
                return labels;
            }, []);
        };
        annotation.chart.labelCollectors.push(annotation.labelCollector);
    };
    /**
     * Set an annotation options.
     * @private
     * @param {Highcharts.AnnotationsOptions} - user options for an annotation
     */
    Annotation.prototype.setOptions = function (userOptions) {
        this.options = merge(this.defaultOptions, userOptions);
    };
    Annotation.prototype.redraw = function (animation) {
        this.linkPoints();
        if (!this.graphic) {
            this.render();
        }
        if (this.clipRect) {
            this.clipRect.animate(this.getClipBox());
        }
        this.redrawItems(this.shapes, animation);
        this.redrawItems(this.labels, animation);
        ControllableMixin.redraw.call(this, animation);
    };
    /**
     * @private
     * @param {Array<Highcharts.AnnotationControllable>} items
     * @param {boolean} [animation]
     */
    Annotation.prototype.redrawItems = function (items, animation) {
        var i = items.length;
        // needs a backward loop
        // labels/shapes array might be modified
        // due to destruction of the item
        while (i--) {
            this.redrawItem(items[i], animation);
        }
    };
    /**
     * @private
     * @param {Array<Highcharts.AnnotationControllable>} items
     */
    Annotation.prototype.renderItems = function (items) {
        var i = items.length;
        while (i--) {
            this.renderItem(items[i]);
        }
    };
    Annotation.prototype.render = function () {
        var renderer = this.chart.renderer;
        this.graphic = renderer
            .g('annotation')
            .attr({
            opacity: 0,
            zIndex: this.options.zIndex,
            visibility: this.options.visible ?
                'visible' :
                'hidden'
        })
            .add();
        this.shapesGroup = renderer
            .g('annotation-shapes')
            .add(this.graphic)
            .clip(this.chart.plotBoxClip);
        this.labelsGroup = renderer
            .g('annotation-labels')
            .attr({
            // hideOverlappingLabels requires translation
            translateX: 0,
            translateY: 0
        })
            .add(this.graphic);
        this.addClipPaths();
        if (this.clipRect) {
            this.graphic.clip(this.clipRect);
        }
        // Render shapes and labels before adding events (#13070).
        this.renderItems(this.shapes);
        this.renderItems(this.labels);
        this.addEvents();
        ControllableMixin.render.call(this);
    };
    /**
     * Set the annotation's visibility.
     * @private
     * @param {boolean} [visible]
     * Whether to show or hide an annotation. If the param is omitted, the
     * annotation's visibility is toggled.
     */
    Annotation.prototype.setVisibility = function (visible) {
        var options = this.options, visibility = pick(visible, !options.visible);
        this.graphic.attr('visibility', visibility ? 'visible' : 'hidden');
        if (!visibility) {
            this.setControlPointsVisibility(false);
        }
        options.visible = visibility;
    };
    Annotation.prototype.setControlPointsVisibility = function (visible) {
        var setItemControlPointsVisibility = function (item) {
            item.setControlPointsVisibility(visible);
        };
        ControllableMixin.setControlPointsVisibility.call(this, visible);
        this.shapes.forEach(setItemControlPointsVisibility);
        this.labels.forEach(setItemControlPointsVisibility);
    };
    /**
     * Destroy the annotation. This function does not touch the chart
     * that the annotation belongs to (all annotations are kept in
     * the chart.annotations array) - it is recommended to use
     * {@link Highcharts.Chart#removeAnnotation} instead.
     * @private
     */
    Annotation.prototype.destroy = function () {
        var chart = this.chart, destroyItem = function (item) {
            item.destroy();
        };
        this.labels.forEach(destroyItem);
        this.shapes.forEach(destroyItem);
        this.clipXAxis = null;
        this.clipYAxis = null;
        erase(chart.labelCollectors, this.labelCollector);
        EventEmitterMixin.destroy.call(this);
        ControllableMixin.destroy.call(this);
        destroyObjectProperties(this, chart);
    };
    /**
     * See {@link Highcharts.Chart#removeAnnotation}.
     * @private
     */
    Annotation.prototype.remove = function () {
        // Let chart.update() remove annoations on demand
        return this.chart.removeAnnotation(this);
    };
    /**
     * Updates an annotation.
     *
     * @function Highcharts.Annotation#update
     *
     * @param {Partial<Highcharts.AnnotationsOptions>} userOptions
     * New user options for the annotation.
     *
     * @return {void}
     */
    Annotation.prototype.update = function (userOptions, redraw) {
        var chart = this.chart, labelsAndShapes = this.getLabelsAndShapesOptions(this.userOptions, userOptions), userOptionsIndex = chart.annotations.indexOf(this), options = merge(true, this.userOptions, userOptions);
        options.labels = labelsAndShapes.labels;
        options.shapes = labelsAndShapes.shapes;
        this.destroy();
        this.constructor(chart, options);
        // Update options in chart options, used in exporting (#9767):
        chart.options.annotations[userOptionsIndex] = options;
        this.isUpdating = true;
        if (pick(redraw, true)) {
            chart.redraw();
        }
        fireEvent(this, 'afterUpdate');
        this.isUpdating = false;
    };
    /* *************************************************************
        * ITEM SECTION
        * Contains methods for handling a single item in an annotation
        **************************************************************** */
    /**
     * Initialisation of a single shape
     * @private
     * @param {Object} shapeOptions - a confg object for a single shape
     */
    Annotation