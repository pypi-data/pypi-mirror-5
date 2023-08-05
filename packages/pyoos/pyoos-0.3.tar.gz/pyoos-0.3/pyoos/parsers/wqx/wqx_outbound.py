from owslib.util import nspath
from owslib.util import testXMLAttribute, testXMLValue
from owslib.crs import Crs
from pyoos.utils.asatime import AsaTime
from pyoos.utils.etree import etree
import pytz

from shapely.geometry import Point as sPoint
from paegan.cdm.dsg.features.base.point import Point
from paegan.cdm.dsg.features.station import Station as Station
from paegan.cdm.dsg.member import Member

def nsp(element_tag, namespace):
    return nspath(element_tag, namespace=namespace)

class WqxToStation(object):
    """
        Convert a WqxOutbound object or WQX string/element to the DSG
    """
    def __init__(self, wqx_metadata, wqx_data):
        if not isinstance(wqx_metadata, WqxOutbound):
            wqx_metadata = WqxOutbound(wqx_metadata)

        if not isinstance(wqx_data, WqxOutbound):
            wqx_data = WqxOutbound(wqx_data)

        if wqx_data.failed or wqx_metadata.failed:
            self.feature = None
        else:
            s = Station()
            s.uid = wqx_metadata.location.id
            s.name = wqx_metadata.location.name
            s.set_property("station_type", wqx_metadata.location.type)
            s.set_property("location_description", wqx_metadata.location.description)
            s.set_property("huc", wqx_metadata.location.huc)
            s.set_property("county", wqx_metadata.location.county)
            s.set_property("state", wqx_metadata.location.state)
            s.set_property("country", wqx_metadata.location.country)
            s.set_property("organization_id", wqx_metadata.organization.id)
            s.set_property("organization_name", wqx_metadata.organization.name)
            s.set_property("vertical_units", wqx_metadata.location.vertical_measure_units)
            s.set_property("horizontal_crs", wqx_metadata.location.horizontal_crs_name)
            s.set_property("vertical_crs", wqx_metadata.location.vertical_crs_name)

            for a in wqx_data.activities:
                p = Point()
                p.time = a.start_time

                for r in a.results:
                    p.add_member(Member(value=r.value, unit=r.units, name=r.name, description=r.short_name, standard=None, quality=r.quality, method_id=a.method_id, method_name=a.method_name))

                s.add_element(p)

            # Now set the station's location
            vertical = 0
            try:
                vertical = float(wqx_metadata.location.vertical_measure_value)
            except:
                pass

            # convert the vertical to meters if it is ft (which it always is)
            if wqx_metadata.location.vertical_measure_units == "ft":
                vertical /= 3.28084
                s.set_property("vertical_units", "m")
            s.location = sPoint(float(wqx_metadata.location.longitude), float(wqx_metadata.location.latitude), vertical)

            self.feature = s

class WqxOutbound(object):
    """
        An WQX formatted <wqx:WQX> block
    """
    def __init__(self, element):
        wqx_ns = "http://qwwebservices.usgs.gov/schemas/WQX-Outbound/2_0/"

        if isinstance(element, str) or isinstance(element, unicode):
            try:
                self._root = etree.fromstring(element)
            except ValueError:
                # Strip out the XML header due to UTF8 encoding declaration
                self._root = etree.fromstring(element[38:])
        else:
            self._root = element

        if hasattr(self._root, 'getroot'):
            self._root = self._root.getroot()

        org = self._root.find(nsp("Organization", wqx_ns))

        self.failed = False
        if org is None:
            self.failed = True
        else:
            self.organization = WqxOrganizationDescription(org.find(nsp("OrganizationDescription",wqx_ns)), wqx_ns)

            self.location = None
            ml = org.find(nsp("MonitoringLocation",wqx_ns))
            if ml is not None:
                self.location = WqxMonitoringLocation(ml, wqx_ns)

            self.activities = []
            for act in org.findall(nsp("Activity", wqx_ns)):
                self.activities.append(WqxActivity(act, wqx_ns))

class WqxActivity(object):
    """
        An WQX formatted <wqx:Activity> block
    """
    def __init__(self, element, wqx_ns):
        self._root = element

        des = self._root.find(nsp("ActivityDescription", wqx_ns))
        if des is not None:
            self.id = testXMLValue(des.find(nsp("ActivityIdentifier", wqx_ns)))
            self.type = testXMLValue(des.find(nsp("ActivityTypeCode", wqx_ns)))
            self.media = testXMLValue(des.find(nsp("ActivityMediaName", wqx_ns)))

        # Date/Time
        sd = testXMLValue(des.find(nsp("ActivityStartDate", wqx_ns)))  # YYYY-MM-DD
        parse_string = "%s" % sd

        st = des.find(nsp("ActivityStartTime", wqx_ns))
        # If no time is defined, skip trying to pull it out and just use the date
        if st is not None:
            t = testXMLValue(st.find(nsp("Time", wqx_ns)))
            tz = testXMLValue(st.find(nsp("TimeZoneCode", wqx_ns)))

            parse_string = "%s %s" % (parse_string, t)
            if tz is not None:
                parse_string = "%s %s" % (parse_string, tz)

        self.start_time = AsaTime.parse(parse_string)    
        if self.start_time.tzinfo is None:
            self.start_time = self.start_time.replace(tzinfo=pytz.utc)

        self.project = testXMLValue(des.find(nsp("ProjectIdentifier", wqx_ns)))
        self.location_id = testXMLValue(des.find(nsp("MonitoringLocationIdentifier", wqx_ns)))
        self.comment = testXMLValue(des.find(nsp("ActivityCommentText", wqx_ns)))

        self.method_id = None
        self.method_name = None
        self.method_context = None
        # Method
        smpl = self._root.find(nsp("SampleDescription", wqx_ns))
        if smpl is not None:
            self.sample_collection_equipment_name = testXMLValue(smpl.find(nsp("SampleCollectionEquipmentName", wqx_ns)))
            smplcol = smpl.find(nsp("SampleCollectionMethod", wqx_ns))
            if smplcol is not None:
                self.method_id = testXMLValue(smplcol.find(nsp("MethodIdentifier", wqx_ns)))
                self.method_context = testXMLValue(smplcol.find(nsp("MethodIdentifierContext", wqx_ns)))
                self.method_name = testXMLValue(smplcol.find(nsp("MethodName", wqx_ns)))
            
        self.results = []
        for res in self._root.findall(nsp("Result", wqx_ns)):
            self.results.append(WqxResult(res, wqx_ns))

class WqxResult(object):
    def __init__(self, element, wqx_ns):
        self._root = element

        des = self._root.find(nsp("ResultDescription", wqx_ns))
        self.name = None
        self.short_name = None
        self.status = None
        self.stastistical_base_code = None
        self.value_type = None
        self.weight_basis = None
        self.time_basis = None
        self.temperature_basis = None
        if des is not None:
            self.name = testXMLValue(des.find(nsp("CharacteristicName", wqx_ns)))
            self.short_name = testXMLValue(des.find(nsp("ResultSampleFractionText", wqx_ns)))
            self.status = testXMLValue(des.find(nsp("ResultStatusIdentifier", wqx_ns)))
            self.stastistical_base_code = testXMLValue(des.find(nsp("StatisticalBaseCode", wqx_ns)))
            self.value_type = testXMLValue(des.find(nsp("ResultValueTypeName", wqx_ns)))
            self.weight_basis = testXMLValue(des.find(nsp("ResultWeightBasisText", wqx_ns)))
            self.time_basis = testXMLValue(des.find(nsp("ResultTimeBasisText", wqx_ns)))
            self.temperature_basis = testXMLValue(des.find(nsp("ResultTemperatureBasisText", wqx_ns)))

        rm = des.find(nsp("ResultMeasure", wqx_ns))
        self.value = None
        self.units = None
        if rm is not None:
            self.value = testXMLValue(rm.find(nsp("ResultMeasureValue", wqx_ns)))
            self.units = testXMLValue(rm.find(nsp("MeasureUnitCode", wqx_ns)))

        qu = des.find(nsp("DataQuality", wqx_ns))
        self.quality = None
        if qu is not None:
            self.quality = testXMLValue(qu.find(nsp("PrecisionValue", wqx_ns)))

        am = self._root.find(nsp("ResultAnalyticalMethod", wqx_ns))
        self.analytical_method_id = None
        self.analytical_method_id_context = None
        if am is not None:
            self.analytical_method_id = testXMLValue(am.find(nsp("MethodIdentifier", wqx_ns)))
            self.analytical_method_id_context = testXMLValue(am.find(nsp("MethodIdentifierContext", wqx_ns)))

        # Skipping <ResultLabInformation> for now.

class WqxOrganizationDescription(object):
    """
        An WQX formatted <wqx:Organization> block
    """
    def __init__(self, element, wqx_ns):
        self._root = element

        self.id = testXMLValue(self._root.find(nsp("OrganizationIdentifier", wqx_ns)))
        self.name = testXMLValue(self._root.find(nsp("OrganizationFormalName", wqx_ns)))

class WqxMonitoringLocation(object):
    """
        An WQX formatted <wqx:MonitoringLocation> block
    """
    def __init__(self, element, wqx_ns):
        self._root = element

        self.id = None
        self.name = None
        self.type = None
        self.description = None
        self.huc = None
        identity = self._root.find(nsp("MonitoringLocationIdentity", wqx_ns))
        if identity is not None:
            self.id = testXMLValue(identity.find(nsp("MonitoringLocationIdentifier", wqx_ns)))
            self.name = testXMLValue(identity.find(nsp("MonitoringLocationName", wqx_ns)))
            self.type = testXMLValue(identity.find(nsp("MonitoringLocationTypeName", wqx_ns)))
            self.description = testXMLValue(identity.find(nsp("MonitoringLocationDescriptionText", wqx_ns)))
            self.huc = testXMLValue(identity.find(nsp("HUCEightDigitCode", wqx_ns)))

        self.latitude = None
        self.longitude = None
        self.map_scale = None
        self.horizontal_collection_method = None
        self.horizontal_crs_name = None
        self.horizontal_crs = None
        self.vertical_crs_name = None
        self.vertical_crs = None
        geo = self._root.find(nsp("MonitoringLocationGeospatial", wqx_ns))
        if geo is not None:
            self.latitude = testXMLValue(geo.find(nsp("LatitudeMeasure", wqx_ns)))
            self.longitude = testXMLValue(geo.find(nsp("LongitudeMeasure", wqx_ns)))
            self.map_scale = testXMLValue(geo.find(nsp("SourceMapScaleNumeric", wqx_ns)))
            self.horizontal_collection_method = testXMLValue(geo.find(nsp("HorizontalCollectionMethodName", wqx_ns)))
            self.horizontal_crs_name = testXMLValue(geo.find(nsp("HorizontalCoordinateReferenceSystemDatumName", wqx_ns)))
            #self.horizontal_crs = Crs("EPSG:" + testXMLValue(geo.find(nsp("HorizontalCoordinateReferenceSystemDatumName", wqx_ns))))
            self.vertical_crs_name = testXMLValue(geo.find(nsp("VerticalCollectionMethodName", wqx_ns)))
            #self.vertical_crs = Crs(testXMLValue("EPSG:" + geo.find(nsp("VerticalCoordinateReferenceSystemDatumName", wqx_ns))))
        
        self.vertical_measure_value = None
        self.vertical_measure_units = None
        vm = geo.find(nsp("VerticalMeasure", wqx_ns))
        if vm is not None:
            self.vertical_measure_value = testXMLValue(vm.find(nsp("MeasureValue", wqx_ns)))
            self.vertical_measure_units = testXMLValue(vm.find(nsp("MeasureUnitCode", wqx_ns)))

        self.country = testXMLValue(geo.find(nsp("CountryCode", wqx_ns)))
        self.state = testXMLValue(geo.find(nsp("StateCode", wqx_ns)))
        self.county = testXMLValue(geo.find(nsp("CountyCode", wqx_ns)))
