import socket
import threading
import time
import requests
import json
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import re

class SmartTVDiscovery:
    def __init__(self, timeout=1.0, scan_range=(1, 254)):
        self.discovered_devices = []
        self.discovery_timeout = 5
        self.request_timeout = timeout
        self.scan_range = scan_range
        self.lock = threading.Lock()

    def send_ssdp_discovery(self):
        """Enhanced SSDP discovery with multiple search targets"""
        search_targets = [
            'upnp:rootdevice',
            'urn:dial-multiscreen-org:service:dial:1',
            'urn:schemas-upnp-org:device:MediaRenderer:1',
            'urn:schemas-upnp-org:device:MediaServer:1',
            'roku:ecp'
        ]
        
        for st in search_targets:
            self._send_ssdp_request(st)

    def _send_ssdp_request(self, search_target):
        ssdp_request = (
            'M-SEARCH * HTTP/1.1\r\n'
            'HOST: 239.255.255.250:1900\r\n'
            'MAN: "ssdp:discover"\r\n'
            f'ST: {search_target}\r\n'
            'MX: 3\r\n\r\n'
        )

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.discovery_timeout)

        try:
            sock.sendto(ssdp_request.encode('utf-8'), ('239.255.255.250', 1900))
            start_time = time.time()
            while time.time() - start_time < self.discovery_timeout:
                try:
                    data, addr = sock.recvfrom(2048)
                    response = data.decode('utf-8', errors='ignore')
                    self._process_ssdp_response(response, addr[0])
                except socket.timeout:
                    break
        except Exception as e:
            print(f"SSDP discovery error: {e}")
        finally:
            sock.close()

    def _process_ssdp_response(self, response, ip):
        """Process SSDP response and extract device information"""
        if 'LOCATION:' in response.upper():
            location = None
            server = None
            
            for line in response.splitlines():
                line_upper = line.upper()
                if line_upper.startswith('LOCATION:'):
                    location = line.split(':', 1)[1].strip()
                elif line_upper.startswith('SERVER:'):
                    server = line.split(':', 1)[1].strip()
            
            if location:
                name = self.get_name_from_location(location, server)
                with self.lock:
                    self.discovered_devices.append({
                        'ip': ip, 
                        'name': name,
                        'method': 'SSDP',
                        'location': location
                    })

    def get_name_from_location(self, location_url, server_info=None):
        """Enhanced device name extraction from UPnP description"""
        try:
            response = requests.get(location_url, timeout=self.request_timeout)
            if response.status_code == 200:
                # Try XML parsing first
                try:
                    root = ET.fromstring(response.text)
                    
                    # Look for friendlyName in various namespaces
                    namespaces = {
                        '': 'urn:schemas-upnp-org:device-1-0',
                        'upnp': 'urn:schemas-upnp-org:device-1-0'
                    }
                    
                    for ns_prefix, ns_uri in namespaces.items():
                        friendly_name = root.find(f'.//{{{ns_uri}}}friendlyName')
                        if friendly_name is not None and friendly_name.text:
                            return friendly_name.text.strip()
                    
                    # Fallback to text search
                    if "<friendlyName>" in response.text:
                        start = response.text.find("<friendlyName>") + len("<friendlyName>")
                        end = response.text.find("</friendlyName>", start)
                        if end > start:
                            return response.text[start:end].strip()
                
                except ET.ParseError:
                    # If XML parsing fails, use text search
                    if "<friendlyName>" in response.text:
                        start = response.text.find("<friendlyName>") + len("<friendlyName>")
                        end = response.text.find("</friendlyName>", start)
                        if end > start:
                            return response.text[start:end].strip()
                
                # Try to extract device info from server header
                if server_info:
                    if 'android' in server_info.lower():
                        return "Android TV"
                    elif 'linux' in server_info.lower() and 'upnp' in server_info.lower():
                        return "Smart TV (Linux)"
                        
        except Exception as e:
            print(f"Error getting name from location {location_url}: {e}")
        
        return "Unknown Smart TV"

    def scan_android_tv(self):
        """Scan for Android TV / Google TV devices"""
        def check(ip):
            # Android TV typically runs on port 6467 for debugging
            # and may have web interfaces on various ports
            ports_to_check = [6467, 8008, 9000, 8080, 80]
            
            for port in ports_to_check:
                try:
                    # Check ADB port (6467) - only check if reachable
                    if port == 6467:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(self.request_timeout)
                        result = sock.connect_ex((ip, port))
                        sock.close()
                        if result == 0:
                            with self.lock:
                                self.discovered_devices.append({
                                    'ip': ip, 
                                    'name': 'Android TV / Google TV',
                                    'method': 'ADB_PORT'
                                })
                            return
                    else:
                        # Check HTTP endpoints
                        url = f"http://{ip}:{port}/"
                        response = requests.get(url, timeout=self.request_timeout)
                        content = response.text.lower()
                        
                        if any(keyword in content for keyword in [
                            'android', 'google tv', 'chromecast', 'cast'
                        ]):
                            device_name = "Android TV / Google TV"
                            if 'chromecast' in content:
                                device_name = "Chromecast / Google TV"
                            
                            with self.lock:
                                self.discovered_devices.append({
                                    'ip': ip, 
                                    'name': device_name,
                                    'method': f'HTTP_{port}'
                                })
                            return
                            
                except Exception:
                    continue
        
        self._scan_ip_range(check)

    def scan_samsung_tv(self):
        """Enhanced Samsung TV detection"""
        def check(ip):
            ports = [8001, 8002, 8080, 26101]
            
            for port in ports:
                try:
                    if port in [8001, 8002]:
                        # WebSocket ports - just check if they're open
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(self.request_timeout)
                        result = sock.connect_ex((ip, port))
                        sock.close()
                        if result == 0:
                            with self.lock:
                                self.discovered_devices.append({
                                    'ip': ip, 
                                    'name': 'Samsung Smart TV',
                                    'method': f'WebSocket_{port}'
                                })
                            return
                    else:
                        url = f"http://{ip}:{port}/"
                        response = requests.get(url, timeout=self.request_timeout)
                        if response.status_code == 200 and 'samsung' in response.text.lower():
                            with self.lock:
                                self.discovered_devices.append({
                                    'ip': ip, 
                                    'name': 'Samsung Smart TV',
                                    'method': f'HTTP_{port}'
                                })
                            return
                except Exception:
                    continue
        
        self._scan_ip_range(check)

    def scan_lg_tv(self):
        """Enhanced LG TV detection"""
        def check(ip):
            ports = [3000, 3001, 36866, 1061]
            
            for port in ports:
                try:
                    url = f"http://{ip}:{port}/"
                    response = requests.get(url, timeout=self.request_timeout)
                    content = response.text.lower()
                    
                    if any(keyword in content for keyword in ['webos', 'lg', 'netcast']):
                        device_name = "LG Smart TV"
                        if 'webos' in content:
                            device_name = "LG WebOS TV"
                        
                        with self.lock:
                            self.discovered_devices.append({
                                'ip': ip, 
                                'name': device_name,
                                'method': f'HTTP_{port}'
                            })
                        return
                        
                except Exception:
                    continue
        
        self._scan_ip_range(check)

    def scan_chromecast(self):
        """Enhanced Chromecast/Google Cast detection"""
        def check(ip):
            ports = [8008, 8009, 8443]
            
            for port in ports:
                try:
                    # Try eureka_info endpoint
                    url = f"http://{ip}:{port}/setup/eureka_info"
                    response = requests.get(url, timeout=self.request_timeout)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            name = data.get("name", "Chromecast")
                            if not name or name == "":
                                name = "Chromecast"
                            
                            with self.lock:
                                self.discovered_devices.append({
                                    'ip': ip, 
                                    'name': name,
                                    'method': 'Eureka'
                                })
                            return
                        except json.JSONDecodeError:
                            pass
                    
                    # Try other Cast endpoints
                    for endpoint in ["/setup/offer", "/setup/scan_wifi"]:
                        try:
                            url = f"http://{ip}:{port}{endpoint}"
                            response = requests.get(url, timeout=self.request_timeout)
                            if response.status_code == 200:
                                with self.lock:
                                    self.discovered_devices.append({
                                        'ip': ip, 
                                        'name': 'Chromecast',
                                        'method': f'Cast_{port}'
                                    })
                                return
                        except Exception:
                            continue
                            
                except Exception:
                    continue
        
        self._scan_ip_range(check)

    def scan_roku(self):
        """Enhanced Roku detection"""
        def check(ip):
            try:
                url = f"http://{ip}:8060/"
                response = requests.get(url, timeout=self.request_timeout)
                
                if response.status_code == 200 and 'roku' in response.text.lower():
                    with self.lock:
                        self.discovered_devices.append({
                            'ip': ip, 
                            'name': 'Roku TV',
                            'method': 'ECP'
                        })
                    return
                    
                # Try device info endpoint
                url = f"http://{ip}:8060/query/device-info"
                response = requests.get(url, timeout=self.request_timeout)
                if response.status_code == 200 and 'roku' in response.text.lower():
                    with self.lock:
                        self.discovered_devices.append({
                            'ip': ip, 
                            'name': 'Roku TV',
                            'method': 'DeviceInfo'
                        })
                        
            except Exception:
                pass
        
        self._scan_ip_range(check)

    def scan_apple_tv(self):
        """Scan for Apple TV devices"""
        def check(ip):
            try:
                # Apple TV typically uses port 7000 for AirPlay
                ports = [7000, 32498, 3689]
                
                for port in ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(self.request_timeout)
                        result = sock.connect_ex((ip, port))
                        sock.close()
                        
                        if result == 0:
                            with self.lock:
                                self.discovered_devices.append({
                                    'ip': ip, 
                                    'name': 'Apple TV',
                                    'method': f'Port_{port}'
                                })
                            return
                    except Exception:
                        continue
                        
            except Exception:
                pass
        
        self._scan_ip_range(check)

    def scan_fire_tv(self):
        """Scan for Amazon Fire TV devices"""
        def check(ip):
            try:
                # Fire TV often uses ADB on port 5555
                ports = [5555, 8080, 8008]
                
                for port in ports:
                    try:
                        if port == 5555:
                            # Check ADB port
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(self.request_timeout)
                            result = sock.connect_ex((ip, port))
                            sock.close()
                            if result == 0:
                                with self.lock:
                                    self.discovered_devices.append({
                                        'ip': ip, 
                                        'name': 'Amazon Fire TV',
                                        'method': 'ADB'
                                    })
                                return
                        else:
                            url = f"http://{ip}:{port}/"
                            response = requests.get(url, timeout=self.request_timeout)
                            if 'amazon' in response.text.lower() or 'fire' in response.text.lower():
                                with self.lock:
                                    self.discovered_devices.append({
                                        'ip': ip, 
                                        'name': 'Amazon Fire TV',
                                        'method': f'HTTP_{port}'
                                    })
                                return
                    except Exception:
                        continue
                        
            except Exception:
                pass
        
        self._scan_ip_range(check)

    def _scan_ip_range(self, scan_fn):
        """Scan IP range with threading"""
        local_ip = self.get_local_ip()
        base_ip = '.'.join(local_ip.split('.')[:-1])
        ip_list = [f"{base_ip}.{i}" for i in range(self.scan_range[0], self.scan_range[1] + 1)]
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(scan_fn, ip_list)

    def get_local_ip(self):
        """Get local IP address"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def get_tv_name_ip_dict(self):
        """Discover all smart TV devices and return as dictionary"""
        print("Starting Smart TV discovery...")
        print(f"Scanning IP range: {self.get_local_ip().rsplit('.', 1)[0]}.{self.scan_range[0]}-{self.scan_range[1]}")
        
        threads = []
        methods = [
            self.send_ssdp_discovery,
            self.scan_android_tv,
            self.scan_samsung_tv,
            self.scan_lg_tv,
            self.scan_chromecast,
            self.scan_roku,
            self.scan_apple_tv,
            self.scan_fire_tv
        ]
        
        # Start all discovery methods
        for method in methods:
            t = threading.Thread(target=method)
            t.daemon = True
            t.start()
            threads.append(t)

        # Wait for all threads to complete
        for t in threads:
            t.join(timeout=20)

        # Deduplicate by IP and create result dictionary
        tv_dict = {}
        seen_ips = set()
        
        for device in self.discovered_devices:
            ip = device['ip']
            name = device.get('name', 'Unknown TV')
            method = device.get('method', 'Unknown')
            
            if ip not in seen_ips:
                # If we have multiple detections for same IP, prefer more specific names
                if ip in [d['ip'] for d in self.discovered_devices]:
                    # Find all devices with this IP
                    same_ip_devices = [d for d in self.discovered_devices if d['ip'] == ip]
                    # Prefer non-generic names
                    best_device = max(same_ip_devices, 
                                    key=lambda x: len(x['name']) if 'Unknown' not in x['name'] else 0)
                    name = best_device['name']
                    method = best_device['method']
                
                tv_dict[f"{name} ({ip})"] = ip
                seen_ips.add(ip)
                print(f"Found: {name} at {ip} (detected via {method})")

        return tv_dict

    def get_detailed_results(self):
        """Get detailed discovery results with all information"""
        self.get_tv_name_ip_dict()  # Run discovery
        
        # Deduplicate by IP
        detailed_results = {}
        seen_ips = set()
        
        for device in self.discovered_devices:
            ip = device['ip']
            if ip not in seen_ips:
                detailed_results[ip] = {
                    'name': device.get('name', 'Unknown TV'),
                    'method': device.get('method', 'Unknown'),
                    'location': device.get('location', None)
                }
                seen_ips.add(ip)
        
        return detailed_results


# Example usage
if __name__ == "__main__":
    print("Enhanced Smart TV Discovery")
    print("=" * 50)
    
    # Create discovery instance with longer timeout for better detection
    discovery = SmartTVDiscovery(timeout=1.5, scan_range=(1, 254))
    
    # Get simple name:IP dictionary
    tvs = discovery.get_tv_name_ip_dict()
    print(tvs)
    
    print("\n" + "=" * 50)
    print("DISCOVERY COMPLETE")
    print("=" * 50)
    
    if tvs:
        print(f"\nFound {len(tvs)} Smart TV(s):")
        for name, ip in tvs.items():
            print(f"  • {name}")
    else:
        print("\nNo Smart TVs found on the network.")
        print("Try:")
        print("1. Ensure TVs are powered on and connected to WiFi")
        print("2. Check if TVs are on the same network")
        print("3. Increase timeout or scan range")
    
    print(f"\nScanned network: {discovery.get_local_ip().rsplit('.', 1)[0]}.1-254")