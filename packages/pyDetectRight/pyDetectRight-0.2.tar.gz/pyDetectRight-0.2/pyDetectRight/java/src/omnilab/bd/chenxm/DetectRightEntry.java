package omnilab.bd.chenxm;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.detectright.core.ConnectionLostException;
import com.detectright.core.DetectRight;
import com.detectright.core.DetectRightException;
import com.detectright.core.DeviceNotFoundException;

import py4j.GatewayServer;


public class DetectRightEntry {
	// default server port
	private static int PORT = 25333;
	
	// main thread of py4j
	public static void main(String[] args) throws DetectRightException, ConnectionLostException, DeviceNotFoundException {
        GatewayServer gatewayServer = new GatewayServer(new DetectRightEntry(), PORT);
        gatewayServer.start();
        System.out.println("Gateway Server Started at port " + PORT);
    }

	/**
	 * Initialize DetectRight instance.
	 */
	public void initializeDetectRight(String dbString) throws DetectRightException, ConnectionLostException{
		DetectRight.initialize("SQLite//"+dbString);
	}
	
	public Map<String, Object> getAllDevices() throws DetectRightException, ConnectionLostException, DeviceNotFoundException{
		return DetectRight.getAllDevices();
	}
	
	public Map<String, Object> getAllDevices(List<String> deviceIDs) throws DetectRightException, ConnectionLostException, DeviceNotFoundException{
		return DetectRight.getAllDevices(deviceIDs);
	}
	
	public Map<String, Object> getProfile() throws DetectRightException, ConnectionLostException, DeviceNotFoundException{
		return DetectRight.getProfile();
	}
	
	public Map<String, Object> getProfile(String schema) throws DetectRightException, ConnectionLostException, DeviceNotFoundException{
		return DetectRight.getProfile(schema);
	}
	
	public Map getProfileFromDevice(String entitytype, String category, String description) throws DetectRightException, ConnectionLostException, DeviceNotFoundException{
		return DetectRight.getProfileFromDevice(entitytype, category, description);
	}
	
	public Map<String, Object> getProfileFromDeviceID(long id) throws DetectRightException, ConnectionLostException, DeviceNotFoundException{
		return DetectRight.getProfileFromDeviceID(id);
	}
	
	public Map<String, Object> getProfileFromHeaders(Map<String, Object> header) throws DetectRightException, ConnectionLostException, DeviceNotFoundException{
		LinkedHashMap<String, Object> lhm = new LinkedHashMap(header);
		return DetectRight.getProfileFromHeaders(lhm);
	}
	
	public Map<String, Object> getProfileFromPhoneID(String id) throws DetectRightException, ConnectionLostException, DeviceNotFoundException{
		return DetectRight.getProfileFromPhoneID(id);
	}
	
	public Map<String, Object> getProfileFromTAC(String tac) throws DetectRightException, ConnectionLostException, DeviceNotFoundException{
		return DetectRight.getProfileFromTAC(tac);
	}
	
	public Map<String, Object> getProfileFromUA(String useragent) throws DetectRightException, ConnectionLostException, DeviceNotFoundException{
		return DetectRight.getProfileFromUA(useragent);
	}
	
	public Map<String, Object> getProfileFromUAProfile(String uap) throws DetectRightException, ConnectionLostException, DeviceNotFoundException{
		return DetectRight.getProfileFromUAProfile(uap);
	}
}
