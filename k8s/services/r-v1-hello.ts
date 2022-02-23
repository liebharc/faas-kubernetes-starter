import { inspect } from 'util';

module.exports = async function (context: any) {
	return {
		status: 200,
		body: inspect(context),
	};
};
