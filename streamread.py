import asyncio
import subprocess

p = subprocess.Popen(["ls","notexistingfile"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

async def do_reading(label, reader,stopwhenany):
    while not reader.at_eof():
        some_bytes = await reader.read(2 ** 16)
        if len(some_bytes):
            e = some_bytes.decode("utf-8")
            #print(label, "\n", e)
            if stopwhenany:
                return (label,e)
    return (label,None)

async def read_pipe(pipe):
    reader = asyncio.StreamReader()
    read_protocol = asyncio.StreamReaderProtocol(reader)
    read_transport, _ = await loop.connect_read_pipe(
                    lambda: read_protocol, pipe)
    return reader

async def read_out(label):
    r= await read_pipe(p.stdout)
    return await do_reading(label, r, False)
    
async def read_err(label):
    r= await read_pipe(p.stderr)
    return await do_reading(label, r, True)
 
async def read_both():
    ro = read_out("stdout")
    re = read_err("stderr")
    pending = [ro,re]
    while True:
        done,pending = await asyncio.wait(pending,return_when=asyncio.FIRST_COMPLETED)
        for d in done:
            r = d.result()
            if r[0] == "stderr" and r[1] is not None:
                print("return err:", r[1])
                for pd in pending:
                    pd.cancel()
                return "I got an error"
        if len(pending) ==0:
            break

loop = asyncio.get_event_loop()
loop.run_until_complete(read_both())
loop.close()
