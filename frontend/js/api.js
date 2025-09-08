// Lightweight API client for the FastAPI backend

const API_BASE_URL = window.API_BASE_URL || window.location.origin;

async function postJSON(path, data) {
	const res = await fetch(`${API_BASE_URL}${path}`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(data),
	});

	const contentType = res.headers.get("content-type") || "";
	const isJSON = contentType.includes("application/json");
	const payload = isJSON ? await res.json() : await res.text();

	if (!res.ok) {
		const msg = isJSON ? payload?.detail || JSON.stringify(payload) : payload;
		throw new Error(msg || `Request failed with ${res.status}`);
	}
	return payload;
}

export async function analyzeQuery(query) {
	return postJSON("/seo/graph", { query });
}

