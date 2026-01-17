const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL

export type ValidateIcsResponse = {
  valid: boolean
  normalized_ics?: string
  errors?: string[]
}

export async function validateIcs(icsText: string): Promise<ValidateIcsResponse> {
  if (!BASE_URL) throw new Error("NEXT_PUBLIC_BACKEND_URL is not set in .env.local")

  const res = await fetch(`${BASE_URL}/calendar/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ics: icsText }),
  })

  if (!res.ok) {
    const msg = await res.text().catch(() => "")
    throw new Error(`Validation failed (${res.status}). ${msg}`)
  }

  return res.json()
}
