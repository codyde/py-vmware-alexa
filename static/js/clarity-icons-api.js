/*
 * Copyright (c) 2016 VMware, Inc. All Rights Reserved.
 * This software is released under MIT license.
 * The full license information can be found in LICENSE in the root directory of this project.
 */
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var DomPurify = require("dompurify");
var iconShapeSources = {};
var ClarityIconsApi = (function () {
    function ClarityIconsApi() {
    }
    Object.defineProperty(ClarityIconsApi, "instance", {
        get: function () {
            if (!ClarityIconsApi.singleInstance) {
                ClarityIconsApi.singleInstance = new ClarityIconsApi();
            }
            return ClarityIconsApi.singleInstance;
        },
        enumerable: true,
        configurable: true
    });
    ClarityIconsApi.prototype.validateName = function (name) {
        if (name.length === 0) {
            throw new Error("Shape name or alias must be a non-empty string!");
        }
        if (/\s/.test(name)) {
            throw new Error("Shape name or alias must not contain any whitespace characters!");
        }
        return true;
    };
    ClarityIconsApi.prototype.sanitizeTemplate = function (template) {
        var allowedTags = [
            "img", "div", "span", "svg", "animate", "animateMotion", "animateTransform",
            "circle", "clipPath", "defs", "desc", "ellipse", "feBlend", "feColorMatrix",
            "feComponentTransfer", "feComposite", "feConvolveMatrix", "feDiffuseLighting",
            "feDisplacementMap", "feDistantLight", "feDropShadow", "feFlood", "feFuncA",
            "feFuncB", "feFuncG", "feFuncR", "feGaussianBlur", "feImage", "feMerge", "feMergeNode",
            "feMorphology", "feOffset", "fePointLight", "feSpecularLighting", "feSpotLight",
            "feTile", "feTurbulence", "filter", "g", "line", "linearGradient", "marker",
            "mask", "mpath", "path", "pattern", "polygon", "polyline", "radialGradient", "rect",
            "stop", "symbol", "text", "textPath", "title", "use", "view"
        ];
        var sanitizeOptions = {
            SAFE_FOR_TEMPLATES: true,
            FORBID_ATTR: ["style"],
            ALLOWED_TAGS: allowedTags,
            ADD_ATTR: ["version", "preserveAspectRatio"]
        };
        return DomPurify.sanitize(template, sanitizeOptions);
    };
    ClarityIconsApi.prototype.setIconTemplate = function (shapeName, shapeTemplate) {
        var trimmedShapeTemplate = shapeTemplate.trim();
        if (this.validateName(shapeName)) {
            //if the shape name exists, delete it.
            if (iconShapeSources[shapeName]) {
                delete iconShapeSources[shapeName];
            }
            iconShapeSources[shapeName] = this.sanitizeTemplate(trimmedShapeTemplate);
        }
    };
    ClarityIconsApi.prototype.setIconAliases = function (templates, shapeName, aliasNames) {
        for (var _i = 0, aliasNames_1 = aliasNames; _i < aliasNames_1.length; _i++) {
            var aliasName = aliasNames_1[_i];
            if (this.validateName(aliasName)) {
                Object.defineProperty(templates, aliasName, {
                    get: function () {
                        return templates[shapeName];
                    },
                    enumerable: true,
                    configurable: true
                });
            }
        }
    };
    ClarityIconsApi.prototype.add = function (icons) {
        if (typeof icons !== "object") {
            throw new Error("The argument must be an object literal passed in the following pattern: \n                { \"shape-name\": \"shape-template\" }");
        }
        for (var shapeName in icons) {
            if (icons.hasOwnProperty(shapeName)) {
                this.setIconTemplate(shapeName, icons[shapeName]);
            }
        }
    };
    ClarityIconsApi.prototype.has = function (shapeName) {
        return !!iconShapeSources[shapeName];
    };
    ClarityIconsApi.prototype.get = function (shapeName) {
        //if shapeName is not given, return all icon templates.
        if (!shapeName) {
            return iconShapeSources;
        }
        if (typeof shapeName !== "string") {
            throw new TypeError("Only string argument is allowed in this method.");
        }
        //if shapeName doesn't exist in the icons templates, throw an error.
        if (!this.has(shapeName)) {
            throw new Error("'" + shapeName + "' is not found in the Clarity Icons set.");
        }
        return iconShapeSources[shapeName];
    };
    ClarityIconsApi.prototype.alias = function (aliases) {
        if (typeof aliases !== "object") {
            throw new Error("The argument must be an object literal passed in the following pattern: \n                { \"shape-name\": [\"alias-name\", ...] }");
        }
        for (var shapeName in aliases) {
            if (aliases.hasOwnProperty(shapeName)) {
                if (iconShapeSources.hasOwnProperty(shapeName)) {
                    //set an alias to the icon if it exists in iconShapeSources.
                    this.setIconAliases(iconShapeSources, shapeName, aliases[shapeName]);
                }
                else if (iconShapeSources.hasOwnProperty(shapeName)) {
                    //set an alias to the icon if it exists in iconShapeSources.
                    this.setIconAliases(iconShapeSources, shapeName, aliases[shapeName]);
                }
                else {
                    throw new Error("The icon '" + shapeName + "' you are trying to set an alias to doesn't exist!");
                }
            }
        }
    };
    return ClarityIconsApi;
}());
exports.ClarityIconsApi = ClarityIconsApi;
