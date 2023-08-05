#-------------------------------------------------------------------------------
# $Id: subset.py 1260 2012-02-10 18:30:16Z meissls $
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Stephan Krause <stephan.krause@eox.at>
#          Stephan Meissl <stephan.meissl@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2011 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------

import re
from django.contrib.gis.geos import Polygon

from eoxserver.core.system import System
from eoxserver.core.exceptions import InvalidExpressionError
from eoxserver.core.util.timetools import getDateTime
from eoxserver.core.util.geotools import getSRIDFromCRSURI
from eoxserver.resources.coverages.filters import (
    BoundedArea, Slice, TimeInterval
)
from eoxserver.services.exceptions import (
    InvalidRequestException, InvalidSubsettingException,
    InvalidAxisLabelException
)

class WCS20SubsetDecoder(object):
    def __init__(self, req, default_crs_id=None):
        self.req = req
        self.default_crs_id = default_crs_id
        
        self.slices = None
        self.trims = None
        
        self.containment = "overlaps"
    
    def _decodeKVPExpression(self, key, value):
        match = re.match(
            r'(\w+)(,([^(]+))?\(([^,]*)(,([^)]*))?\)', value
        )
        if match is None:
            raise InvalidRequestException(
                "Invalid subsetting operation '%s=%s'" % (key, value),
                "InvalidSubsetting",
                key
            )
        else:
            axis_label = match.group(1)
            crs = match.group(3)
            
            if match.group(6) is not None:
                subset = (axis_label, crs, match.group(4), match.group(6))
                subset_type = "trim"
            else:
                subset = (axis_label, crs, match.group(4))
                subset_type = "slice"

        return (subset, subset_type)
    
    def _decodeKVP(self):
        trims = []
        slices = []
        
        for key, values in self.req.getParams().items():
            if key.startswith("subset"):
                for value in values:
                    subset, subset_type = \
                        self._decodeKVPExpression(key, value)
                    
                    if subset_type == "trim":
                        trims.append(subset)
                    else:
                        slices.append(subset)
        
        self.trims = trims
        self.slices = slices
    
    def _decodeXML(self):
        trims = []
        slices = []
        
        slice_elements = self.req.getParamValue("slices")
        trim_elements = self.req.getParamValue("trims")
        
        for slice_element in slice_elements:
            axis_label = slice_element.getElementsByTagName("wcs:Dimension")[0].firstChild.data
            crs = None
            slice_point = slice_element.getElementsByTagName("wcs:SlicePoint")[0].firstChild.data
            
            slices.append((axis_label, crs, slice_point))
            
        for trim_element in trim_elements:
            axis_label = trim_element.getElementsByTagName("wcs:Dimension")[0].firstChild.data
            crs = None
            trim_low = trim_element.getElementsByTagName("wcs:TrimLow")[0].firstChild.data
            trim_high = trim_element.getElementsByTagName("wcs:TrimHigh")[0].firstChild.data
        
            trims.append((axis_label, crs, trim_low, trim_high))
            
        self.slices = slices
        self.trims = trims
    
    def _decode(self):
        if self.req.getParamType() == "kvp":
            self._decodeKVP()
        else:
            self._decodeXML()
        
        try:
            self.containment = \
                self.req.getParamValue("containment", "overlaps")
        except:
            pass
    
    def _getSliceExpression(self, slice):
        axis_label = slice[0]
        
        if axis_label in ("t", "time", "phenomenonTime"):
            return self._getTimeSliceExpression(slice)
        else:
            return self._getSpatialSliceExpression(slice)
        
    def _getTimeSliceExpression(self, slice):
        axis_label = slice[0]
        
        if slice[1] is not None and \
           slice[1] != "http://www.opengis.net/def/trs/ISO-8601/0/Gregorian+UTC":
            raise InvalidSubsettingException(
                "Time reference system '%s' not recognized. Please use UTC." %\
                slice[1]
            )
        
        if self.req.getParamType() == "kvp":
            if not slice[2].startswith('"') and slice[2].endswith('"'):
                raise InvalidSubsettingException(
                    "Date/Time tokens have to be enclosed in quotation marks (\")"
                )
            else:
                dt_str = slice[2].strip('"')
        else:
            dt_str = slice[0] # TODO: FIXME
        
        try:
            slice_point = getDateTime(dt_str)
        except:
            raise InvalidSubsettingException(
                "Could not convert slice point token '%s' to date/time." %\
                dt_str
            )
        
        return System.getRegistry().getFromFactory(
            "resources.coverages.filters.CoverageExpressionFactory",
            {"op_name": "time_slice", "operands": (slice_point,)}
        )
        
    def _getSpatialSliceExpression(self, slice):
        axis_label = slice[0]
        
        if slice[1] is None:
            crs_id = self.default_crs_id
        else:
            try:
                crs_id = getSRIDFromCRSURI(slice[1])
            except:
                raise InvalidSubsettingException(
                    "Unrecognized CRS URI '%s'" % slice[1]
                )
        
        try:
            slice_point = float(slice[2])
        except:
            raise InvalidSubsettingException(
                "Could not convert slice point token '%s' to number." %\
                slice[2]
            )
        
        return System.getRegistry().getFromFactory(
            "resources.coverages.filters.CoverageExpressionFactory",
            {
                "op_name": "spatial_slice",
                "operands": (Slice(
                    axis_label = axis_label,
                    crs_id = crs_id,
                    slice_point = slice_point
                ),)
            }
        )
    
    def _getTrimExpressions(self, trims):
        time_intv, crs_id, x_bounds, y_bounds = self._decodeTrims(trims)

        if self.containment.lower() == "overlaps":
            op_part = "intersects"
        elif self.containment.lower() == "contains":
            op_part = "within"
        else:
            raise InvalidParameterException(
                "Unknown containment mode '%s'." % self.containment
            )
        
        filter_exprs = []
            
        if time_intv is not None:
            filter_exprs.append(System.getRegistry().getFromFactory(
                "resources.coverages.filters.CoverageExpressionFactory",
                {
                    "op_name": "time_%s" % op_part,
                    "operands": (time_intv,)
                }
            ))
        
        if x_bounds is None and y_bounds is None:
            pass
        else:
            # NOTE: cannot filter w.r.t. imageCRS
            if crs_id != "imageCRS":
                if x_bounds is None:
                    x_bounds = ("unbounded", "unbounded")
                
                if y_bounds is None:
                    y_bounds = ("unbounded", "unbounded")
                
                try:
                    area = BoundedArea(
                        crs_id,
                        x_bounds[0],
                        y_bounds[0],
                        x_bounds[1],
                        y_bounds[1]
                    )
                except InvalidExpressionError, e:
                    raise InvalidSubsettingException(str(e))
                    
                filter_exprs.append(System.getRegistry().getFromFactory(
                    "resources.coverages.filters.CoverageExpressionFactory",
                    {
                        "op_name": "footprint_%s_area" % op_part,
                        "operands": (area,)
                    }
                ))
        
        return filter_exprs

    def _decodeTrims(self, trims):
        time_intv = None
        crs_id = None
        x_bounds = None
        y_bounds = None
        
        for trim in trims:
            if trim[0] in ("t", "time", "phenomenonTime"):
                if time_intv is None:
                    begin = self._getDateTimeBound(trim[2])
                    end = self._getDateTimeBound(trim[3])
                    
                    try:
                        time_intv = TimeInterval(begin, end)
                    except Exception, e:
                        raise InvalidSubsettingException(str(e))
                else:
                    raise InvalidSubsettingException(
                        "Multiple definitions for time subsetting."
                    )
            elif trim[0] in ("x", "lon", "Lon", "long", "Long"):
                
                if x_bounds is None:
                    new_crs_id = self._getCRSID(trim[1])
                    
                    if crs_id is None:
                        crs_id = new_crs_id
                    elif crs_id != new_crs_id:
                        raise InvalidSubsettingException(
                            "CRSs for multiple spatial trims must be the same."
                        )
                        
                    x_bounds = (
                        self._getCoordinateBound(crs_id, trim[2]),
                        self._getCoordinateBound(crs_id, trim[3])
                    )
                else:
                    raise InvalidSubsettingException(
                        "Multiple definitions for first spatial axis subsetting."
                    )
            elif trim[0] in ("y", "lat", "Lat"):
                if y_bounds is None:
                    new_crs_id = self._getCRSID(trim[1])
                    
                    if crs_id is None:
                        crs_id = new_crs_id
                    elif crs_id != new_crs_id:
                        raise InvalidSubsettingException(
                            "CRSs for multiple spatial trims must be the same."
                        )
                    
                    y_bounds = (
                        self._getCoordinateBound(crs_id, trim[2]),
                        self._getCoordinateBound(crs_id, trim[3])
                    )
                else:
                    raise InvalidSubsettingException(
                        "Multiple definitions for second spatial axis subsetting."
                    )
            else:
                raise InvalidAxisLabelException(
                    "Invalid axis label '%s'." % trim[0]
                )
        
        return (time_intv, crs_id, x_bounds, y_bounds)
        
    
    def _getDateTimeBound(self, token):
        if token is None:
            return "unbounded"
        else:
            if self.req.getParamType() == "kvp":
                if not token.startswith('"') or not token.endswith('"'):
                    raise InvalidSubsettingException(
                        "Date/Time tokens have to be enclosed in quotation marks (\")"
                    )
                else:
                    dt_str = token.strip('"')
            else:
                dt_str = token
            
            try:
                return getDateTime(dt_str)
            except:
                raise InvalidSubsettingException(
                    "Cannot convert token '%s' to Date/Time." % token
                )
    
    def _getCoordinateBound(self, crs_id, token):
        if token is None:
            return "unbounded"
        elif crs_id != "imageCRS":
            try:
                return float(token)
            except:
                raise InvalidSubsettingException(
                    "Cannot convert token '%s' to number." % token
                )
        else:
            try:
                return int(token)
            except:
                raise InvalidSubsettingException(
                    "Cannot convert token '%s' to integer." % token
                )
    
    def _getCRSID(self, crs_expr):
        if crs_expr is None:
            return self.default_crs_id
        else:
            try:
                return getSRIDFromCRSURI(crs_expr)
            except Exception, e:
                raise InvalidSubsettingException(e.msg)
    
    def _get_image_extent(self, x_bounds, y_bounds, x_size, y_size):
        if x_bounds[0] == "unbounded":
            minx = 0
        else:
            minx = x_bounds[0]
        
        if x_bounds[1] == "unbounded":
            maxx = x_size
        else:
            maxx = x_bounds[1]
            
        if y_bounds[0] == "unbounded":
            miny = 0
        else:
            miny = y_bounds[0]
    
        if y_bounds[1] == "unbounded":
            maxy = y_size
        else:
            maxy = y_bounds[1]
        
        return (minx, miny, maxx, maxy)

    def _get_geo_extent(self, crs_id, x_bounds, y_bounds, footprint):
        fp_minx, fp_miny, fp_maxx, fp_maxy = \
            footprint.transform(crs_id, True).extent
            
        if x_bounds[0] == "unbounded":
            minx = fp_minx
        else:
            minx = x_bounds[0]
        
        if x_bounds[1] == "unbounded":
            maxx = fp_maxx
        else:
            maxx = x_bounds[1]
            
        if y_bounds[0] == "unbounded":
            miny = fp_miny
        else:
            miny = y_bounds[0]
    
        if y_bounds[1] == "unbounded":
            maxy = fp_maxy
        else:
            maxy = y_bounds[1]

        return (minx, miny, maxx, maxy)
    
    def getFilterExpressions(self):
        self._decode()
        
        filter_exprs = []
        
        for slice in self.slices:
            filter_exprs.append(self._getSliceExpression(slice))
        
        filter_exprs.extend(self._getTrimExpressions(self.trims))
        return filter_exprs
    
    def getBoundingPolygon(self, footprint, srid, size_x, size_y, extent):
        self._decode()
        
        time_intv, crs_id, x_bounds, y_bounds = \
            self._decodeTrims(self.trims)
        
        if x_bounds is None and y_bounds is None:
            return None
        
        if x_bounds is None:
            x_bounds = ("unbounded", "unbounded")
        if y_bounds is None:
            y_bounds = ("unbounded", "unbounded")
        
        if crs_id == "imageCRS":
            if x_bounds[0] == "unbounded":
                minx = extent[0]
            else:
                l = max(float(x_bounds[0]) / float(size_x), 0.0)
                minx = extent[0] + l * (extent[2] - extent[0])
            
            if y_bounds[0] == "unbounded":
                miny = extent[1]
            else:
                l = max(float(y_bounds[0]) / float(size_y), 0.0)
                miny = extent[3] - l * (extent[3] - extent[1])
            
            if x_bounds[1] == "unbounded":
                maxx = extent[2]
            else:
                l = min(float(x_bounds[1]) / float(size_x), 1.0)
                maxx = extent[0] + l * (extent[2] - extent[0])
            
            if y_bounds[1] == "unbounded":
                maxy = extent[3]
            else:
                l = min(float(y_bounds[1]) / float(size_y), 1.0)
                maxy = extent[3] - l * (extent[3] - extent[1])
            
            poly = Polygon.from_bbox((minx, miny, maxx, maxy))
            poly.srid = srid
        
        else:
            fp_minx, fp_miny, fp_maxx, fp_maxy = \
                footprint.transform(crs_id, True).extent
            
            if x_bounds[0] == "unbounded":
                minx = fp_minx
            else:
                minx = max(fp_minx, x_bounds[0])
            
            if y_bounds[0] == "unbounded":
                miny = fp_miny
            else:
                miny = max(fp_miny, y_bounds[0])
            
            if x_bounds[1] == "unbounded":
                maxx = fp_maxx
            else:
                maxx = min(fp_maxx, x_bounds[1])
            
            if y_bounds[1] == "unbounded":
                maxy = fp_maxy
            else:
                maxy = min(fp_maxy, y_bounds[1])
            
            poly = Polygon.from_bbox((minx, miny, maxx, maxy))
            poly.srid = crs_id
            
        return poly

    def getSubset(self, x_size, y_size, footprint):
        self._decode()
        
        time_intv, crs_id, x_bounds, y_bounds = \
            self._decodeTrims(self.trims)
        
        if x_bounds is None and y_bounds is None:
            return None

        if x_bounds is None:
            x_bounds = ("unbounded", "unbounded")
        if y_bounds is None:
            y_bounds = ("unbounded", "unbounded")
            
        if crs_id == "imageCRS":
            minx, miny, maxx, maxy = self._get_image_extent(x_bounds, y_bounds, x_size, y_size)
        else:
            minx, miny, maxx, maxy = self._get_geo_extent(crs_id, x_bounds, y_bounds, footprint)
        
        return BoundedArea(
            crs_id = crs_id,
            minx = minx,
            miny = miny,
            maxx = maxx,
            maxy = maxy
        )
            
