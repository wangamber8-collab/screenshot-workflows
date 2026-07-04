import { createClient } from 'jsr:@supabase/supabase-js@2'

Deno.serve(async (req) => {
  const {user_id} = await req.json()

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  const { data: screenshots, error: fetchError } = await supabase
    .from('screenshots')
    .select('storage_path')
    .eq('user_id', user_id)
  
  if(fetchError) {
    return new Response(JSON.stringify({ error: fetchError.message }), { status: 400})
  }

  if (screenshots && screenshots.length > 0) {
    const paths = screenshots.map(s => s.storage_path)
    const { error: removeError } = await supabase.storage
      .from('test_screenshots') //replace with actual bucket name
      .remove(paths)
    
    if(removeError) {
      return new Response(JSON.stringify({ error: removeError.message}), { status: 400})
    }
  }

  await supabase.from('screenshots').delete().eq('user_id', user_id)
  await supabase.from('workflow_sets').delete().eq('user_id', user_id)
  //await supabase.from('input').delete().eq('user_id', user_id)  <-- assuming user id info for each screenshot is stored in a separate table

  return new Response(JSON.stringify({ success: true}), {status: 200})
})