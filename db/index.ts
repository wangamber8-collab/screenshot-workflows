import { createClient } from 'jsr:@supabase/supabase-js@2'

Deno.serve(async (req) => {
  const payload = await req.json()
  const record = payload.record

  //replace with actual bucket name
  if(record.bucket_id != 'test-screenshots') {
    return new Response(JSON.stringify({skipped: true}), {status : 200})
  }

  const name = record.name

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  //assuming input file to user mapping information is stored in a separate table
  const { data : inputRow, error : lookupError } = await supabase
    .from('input')
    .select('user_id') //replace with actual fields
    .eq('image_file', name)
    .single()
  
  if (lookupError || !inputRow) {
    return new Response(JSON.stringify({ error : 'user lookup failed'}), {status : 400})
  }

  const { data : signed, error : signedError } = await supabase
    .storage
    .from('test-screenshots')
    .createSignedUrl(name, 60 * 60 * 24 * 7)
  
  if(signedError || !signed) {
    return new Response(JSON.stringify({error: 'signing failed'}), {status: 400})
  }

  const {data : row, error : insertError} = await supabase
    .from('screenshots')
    .insert({ image_url: signed.signedUrl, user_id: inputRow.user_id})
    .select()
    .single()
  
  if(insertError) {
    return new Response(JSON.stringify({error : insertError.message}), {status : 400})
  }

  const res = await fetch("VALUE_HERE", { //fill in with deployed fastapi route or replace this if using different redis provider
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-webhook-secret": Deno.env.get("WEBHOOK_SECRET")!,
    },
    body: JSON.stringify({ screenshot_id: row.id})
  });

  if(!res.ok) {
    const error = await res.json()
    return new Response(JSON.stringify(error), {status : res.status})
  }

  return new Response(JSON.stringify({success : true}), {status : 200})

});