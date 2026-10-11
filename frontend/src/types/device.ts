export interface Device {
  id: number;
  name: string;
  host: string;
  port: number;
  device_type: 'cisco_ios';
  username: string;
  site: string | null;
  path_ping_target: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DeviceCreatePayload {
  name: string;
  host: string;
  port: number;
  device_type: 'cisco_ios';
  username: string;
  password: string;
  secret?: string | null;
  site?: string | null;
  path_ping_target?: string | null;
  is_active?: boolean;
}

export interface DeviceUpdatePayload {
  name?: string;
  host?: string;
  port?: number;
  device_type?: 'cisco_ios';
  username?: string;
  password?: string;
  secret?: string | null;
  site?: string | null;
  path_ping_target?: string | null;
  is_active?: boolean;
}

export interface DevicePage {
  items: Device[];
  total: number;
  offset: number;
  limit: number;
}

export interface ConnectionTestResult {
  device_id: number;
  reachable: boolean;
  message: string;
}
