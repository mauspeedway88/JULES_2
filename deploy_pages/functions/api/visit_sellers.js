export async function onRequestPost(context) {
    const { request, env } = context;
    try {
        const cf = request.cf || {};
        const country = cf.country || "SV";
        const city = cf.city || "San Salvador";
        const latitude = cf.latitude ? parseFloat(cf.latitude) : 13.6929;
        const longitude = cf.longitude ? parseFloat(cf.longitude) : -89.2181;
        if (!env.DB) return new Response(JSON.stringify({ error: 'No DB' }), { status: 500, headers: { "Access-Control-Allow-Origin": "*" } });
        
        // AUTO-CREAR TABLA SI NO EXISTE
        await env.DB.prepare(`
            CREATE TABLE IF NOT EXISTS visits_sellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                city TEXT,
                country TEXT,
                latitude REAL,
                longitude REAL,
                timestamp DATETIME DEFAULT (datetime('now', 'localtime'))
            )
        `).run();

        await env.DB.prepare(
            "INSERT INTO visits_sellers (city, country, latitude, longitude) VALUES (?, ?, ?, ?)"
        ).bind(city, country, latitude, longitude).run();
        return new Response(JSON.stringify({ success: true }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
    } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { "Access-Control-Allow-Origin": "*" } });
    }
}
export async function onRequestGet(context) {
    const { env } = context;
    try {
        if (!env.DB) return new Response(JSON.stringify({ visits: [], error: 'No DB' }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
        
        // AUTO-CREAR TABLA SI NO EXISTE
        await env.DB.prepare(`
            CREATE TABLE IF NOT EXISTS visits_sellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                city TEXT,
                country TEXT,
                latitude REAL,
                longitude REAL,
                timestamp DATETIME DEFAULT (datetime('now', 'localtime'))
            )
        `).run();

        const { results } = await env.DB.prepare("SELECT * FROM visits_sellers ORDER BY timestamp DESC").all();
        return new Response(JSON.stringify({ visits: results || [] }), {
            headers: { "Content-Type": "application/json", "Cache-Control": "no-store", "Access-Control-Allow-Origin": "*" }
        });
    } catch (err) {
        return new Response(JSON.stringify({ visits: [], error: err.message }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
    }
}
