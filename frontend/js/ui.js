const loadingEl = document.getElementById("loading");
const resultPre = document.getElementById("result");
const errorEl = document.getElementById("error");

export function setLoading(isLoading) {
	if (!loadingEl) return;
	loadingEl.hidden = !isLoading;
}

export function showResult(result) {
	if (!resultPre) return;
	const text = typeof result === "string" ? result : JSON.stringify(result, null, 2);
	resultPre.textContent = text;
}

export function showError(message) {
	if (!errorEl) return;
	errorEl.hidden = false;
	errorEl.textContent = message;
}

export function clearOutput() {
	if (resultPre) resultPre.textContent = "";
	if (errorEl) {
		errorEl.textContent = "";
		errorEl.hidden = true;
	}
}

