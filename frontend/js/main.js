import { analyzeQuery } from "./api.js";
import { setLoading, showError, showResult, clearOutput } from "./ui.js";

const form = document.getElementById("analyzeForm");
const input = document.getElementById("queryInput");

form?.addEventListener("submit", async (e) => {
	e.preventDefault();
	const query = (input?.value || "").trim();
	if (!query) {
		showError("Please enter a query.");
		return;
	}

	clearOutput();
	setLoading(true);
	try {
		const data = await analyzeQuery(query);
		// Expecting { message: string, result: any }
		showResult(data?.result ?? data);
	} catch (err) {
		showError(err?.message || String(err));
	} finally {
		setLoading(false);
	}
});

