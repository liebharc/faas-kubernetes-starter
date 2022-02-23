import * as fs from 'fs';
import axios from 'axios';
import * as jwt from 'jsonwebtoken';
import * as jwkToPem from 'jwk-to-pem';
import { ClientConfig } from 'pg';

export interface FissionContext {
	request: {
		body: any;
		headers: Record<string, string>;
		method: string;
		query: Record<string, string>;
	};
}

export interface FissionResponse {
	status: number;
	body: string;
	headers?: Record<string, string>;
}

let publicKeys: any[] = [];

async function fetchPublicKeys(): Promise<any[]> {
	if (publicKeys.length > 0) {
		console.log('Using cached public keys');
		return publicKeys;
	}

	const authUrl = fs.readFileSync(
		'/secrets/default/ravensecrets/AUTH_URL',
		'utf8'
	);
	const realm = 'CockatooT7';
	const verifyUrl = `${authUrl}/auth/realms/${realm}/protocol/openid-connect/certs`;
	console.log('Getting public keys from: ' + verifyUrl);
	const keycloakResp = await axios.get(verifyUrl);
	publicKeys = keycloakResp.data.keys;
	console.log('Fetched public keys: ' + JSON.stringify(publicKeys));
	return publicKeys;
}

export async function verifyToken(token: string): Promise<string | null> {
	const publicKeys = await fetchPublicKeys();
	const pem = jwkToPem(publicKeys[0]);
	const bearer = 'Bearer ';
	if (!token.startsWith(bearer)) {
		console.warn("Invalid token: doesn't start with 'Bearer': " + token);
		return null;
	}

	token = token.substring(bearer.length);
	const result = jwt.verify(token, pem, { complete: false });
	if (typeof result === 'string') {
		return result;
	}

	if (result.sub && typeof result.sub === 'string') {
		return result.sub;
	}

	console.error('Unknown jwt token: ' + JSON.stringify(result));
	return null;
}

export function addCorsHeader(result: {
	statusCode: number;
	body: string;
}): FissionResponse {
	return {
		status: result.statusCode,
		body: result.body,
		headers: {
			'Content-type': 'application/json',
			'Access-Control-Allow-Credentials': 'true',
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': '*',
			'Access-Control-Allow-Headers':
				'Content-Type, Authorization, Clientversion, Content-Length, X-Requested-With',
		},
	};
}

export function getDatabaseConnectionDetails(): ClientConfig {
	return {
		host: fs.readFileSync('/secrets/default/ravensecrets/DB_HOST', 'utf8'),
		database: fs.readFileSync(
			'/secrets/default/ravensecrets/DB_DATABASE',
			'utf8'
		),
		user: fs.readFileSync('/secrets/default/ravensecrets/DB_USER', 'utf8'),
		password: fs.readFileSync(
			'/secrets/default/ravensecrets/DB_PASSWORD',
			'utf8'
		),
	};
}
