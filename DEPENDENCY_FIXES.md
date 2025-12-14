# Dependency Fixes - December 2024

## Issues Fixed

### 1. Logfire Configuration Error
**Error**: `configure() got unexpected keyword arguments: environment`

**Cause**: Logfire 0.54.0+ deprecated the `environment` parameter

**Fix**: Removed `environment` parameter from `logfire.configure()` call

### 2. Supabase/httpx Compatibility Error  
**Error**: `Client.__init__() got an unexpected keyword argument 'proxy'`

**Cause**: 
- `supabase==2.3.4` required `httpx<0.26`
- `gotrue` (supabase dependency) passed `proxy` argument
- `httpx 0.25.2` doesn't support `proxy` parameter
- Python 3.13 compatibility issues

**Fix**: Upgraded all packages to latest compatible versions

## Updated Dependencies

| Package | Old Version | New Version | Reason |
|---------|-------------|-------------|--------|
| **supabase** | 2.3.4 | 2.25.1 | Fix gotrue proxy issue, httpx 0.27 support |
| **python-telegram-bot** | 20.7 | 21.9 | httpx 0.27 compatibility |
| **httpx** | 0.25.2 | 0.27.2 | Required by supabase 2.25.1 |
| **pydantic** | 2.9.2 | 2.12.5 | Auto-upgraded with supabase |
| **pydantic-settings** | 2.6.1 | 2.12.0 | Pydantic 2.12 compatibility |

## Verification

```bash
# Check versions
conda activate cozyberries-telegram-bot
pip list | grep -E "(supabase|telegram|httpx|pydantic|logfire)"
```

Expected output:
```
supabase                  2.25.1
python-telegram-bot       21.9
httpx                     0.27.2
pydantic                  2.12.5
pydantic-settings         2.12.0
logfire                   0.54.0
```

## Testing

```bash
# Test imports
python -c "from telegram import Bot; from supabase import create_client; import logfire; print('✅ All imports working')"

# Test FastAPI server
./TEST_LOGFIRE_LOCAL.sh
```

## Breaking Changes

### python-telegram-bot 20.7 → 21.9
- Mostly backward compatible
- Minor API improvements
- No breaking changes for our usage

### supabase 2.3.4 → 2.25.1  
- Package structure changed:
  - Old: `gotrue`, `storage3`, `supafunc`, `realtime`, `postgrest` as separate packages
  - New: `supabase-auth`, `supabase-functions` (integrated)
- API remains compatible
- Better type hints

### pydantic 2.9 → 2.12
- Fully backward compatible
- Performance improvements
- Better error messages

## Files Modified

1. **app/logging_config.py**
   - Removed `environment` parameter from `logfire.configure()`
   
2. **requirements.txt**
   - Updated all package versions

3. **conda environment**
   - Re-installed with new versions

## Rollback (if needed)

```bash
# Not recommended, but if needed:
pip install \
  python-telegram-bot==20.7 \
  supabase==2.3.4 \
  httpx==0.25.2 \
  pydantic==2.9.2 \
  pydantic-settings==2.6.1
```

**Note**: This will bring back the original errors!

## Production Deployment

```bash
# Update Vercel environment
vercel --prod

# Vercel will automatically use new requirements.txt
```

## Future Maintenance

- Keep dependencies updated regularly
- Test locally before deploying
- Check for breaking changes in release notes
- Update this document with any new issues

---

**Last Updated**: December 14, 2024  
**Python Version**: 3.13.11  
**Conda Environment**: cozyberries-telegram-bot
